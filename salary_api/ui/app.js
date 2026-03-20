const responseBox = document.getElementById("responseBox");
const employeeTableBody = document.getElementById("employeeTableBody");
const employeeCount = document.getElementById("employeeCount");
const changeRequestTableBody = document.getElementById("changeRequestTableBody");
const changeRequestCount = document.getElementById("changeRequestCount");
const changeRequestDetails = document.getElementById("changeRequestDetails");
const openQuestionsContainer = document.getElementById("openQuestionsContainer");
const requestSummaryModal = new bootstrap.Modal(document.getElementById("requestSummaryModal"));
const questionsModal = new bootstrap.Modal(document.getElementById("questionsModal"));
const previewModal = new bootstrap.Modal(document.getElementById("previewModal"));
const requestSummaryModalContent = document.getElementById("requestSummaryModalContent");
const questionsModalMeta = document.getElementById("questionsModalMeta");
const questionsModalContent = document.getElementById("questionsModalContent");
const previewModalContent = document.getElementById("previewModalContent");
const finalApproveBtn = document.getElementById("finalApproveBtn");
const changeRequestForm = document.getElementById("createChangeRequestForm");
let activePreviewRequestId = null;

function todayIsoDate() {
  return new Date().toISOString().slice(0, 10);
}

function setDefaultChangeRequestDate() {
  const dateInput = changeRequestForm.elements.namedItem("request_date");
  if (dateInput && !dateInput.value) {
    dateInput.value = todayIsoDate();
  }
}

function showResponse(title, data) {
  responseBox.textContent = `${title}\n\n${JSON.stringify(data, null, 2)}`;
}

async function apiCall(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  let payload = null;
  const text = await response.text();
  try {
    payload = text ? JSON.parse(text) : {};
  } catch {
    payload = { raw: text };
  }

  return {
    ok: response.ok,
    status: response.status,
    payload,
  };
}

function renderEmployees(employees) {
  employeeCount.textContent = employees.length;
  employeeTableBody.innerHTML = "";

  if (!employees.length) {
    employeeTableBody.innerHTML = "<tr><td colspan='5' class='text-center text-muted'>No employees found.</td></tr>";
    return;
  }

  for (const emp of employees) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${emp.id}</td>
      <td>${emp.full_name}</td>
      <td>${emp.job_title}</td>
      <td>${emp.country}</td>
      <td>${emp.salary}</td>
    `;
    employeeTableBody.appendChild(row);
  }
}

async function refreshEmployees() {
  const result = await apiCall("/employees");
  if (result.ok) {
    renderEmployees(result.payload);
  }
  showResponse("GET /employees", { status: result.status, body: result.payload });
}

function renderChangeRequests(changeRequests) {
  changeRequestCount.textContent = changeRequests.length;
  changeRequestTableBody.innerHTML = "";

  if (!changeRequests.length) {
    changeRequestTableBody.innerHTML =
      "<tr><td colspan='5' class='text-center text-muted'>No change requests found.</td></tr>";
    return;
  }

  for (const request of changeRequests) {
    const row = document.createElement("tr");
    const previewDisabled = request.status !== "answered" && request.status !== "preview_ready";
    const rejectDisabled = request.status === "rejected";
    row.innerHTML = `
      <td>${request.id}</td>
      <td>${request.request_date}</td>
      <td><button class="btn btn-link p-0 topicLink" data-request-id="${request.id}">${request.topic}</button></td>
      <td>${request.status}</td>
      <td><button class="btn btn-link p-0 questionsLink" data-request-id="${request.id}">${request.open_questions.length}</button></td>
      <td>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-outline-primary previewBtn" data-request-id="${request.id}" ${previewDisabled ? "disabled" : ""}>Preview</button>
          <button class="btn btn-sm btn-outline-danger rejectBtn" data-request-id="${request.id}" ${rejectDisabled ? "disabled" : ""}>Reject</button>
        </div>
      </td>
    `;
    changeRequestTableBody.appendChild(row);
  }

  document.querySelectorAll(".topicLink").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const requestId = event.currentTarget.dataset.requestId;
      const result = await apiCall(`/change-requests/${requestId}`);
      if (!result.ok) {
        showResponse(`GET /change-requests/${requestId}`, { status: result.status, body: result.payload });
        return;
      }
      const request = result.payload;
      requestSummaryModalContent.innerHTML = `
        <div class="mb-2"><strong>Date:</strong> ${request.request_date}</div>
        <div class="mb-2"><strong>Topic:</strong> ${request.topic}</div>
        <div><strong>Request Summary:</strong><br>${request.request_summary}</div>
      `;
      requestSummaryModal.show();
    });
  });

  document.querySelectorAll(".questionsLink").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const requestId = event.currentTarget.dataset.requestId;
      await loadChangeRequest(requestId, true);
    });
  });

  document.querySelectorAll(".previewBtn").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const requestId = event.currentTarget.dataset.requestId;
      const result = await apiCall(`/change-requests/${requestId}/preview`, { method: "POST" });
      showResponse(`POST /change-requests/${requestId}/preview`, {
        status: result.status,
        body: result.payload,
      });
      if (!result.ok) {
        return;
      }
      activePreviewRequestId = requestId;
      renderPreview(result.payload);
      previewModal.show();
      await refreshChangeRequests();
    });
  });

  document.querySelectorAll(".rejectBtn").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const requestId = event.currentTarget.dataset.requestId;
      const result = await apiCall(`/change-requests/${requestId}/reject`, { method: "POST" });
      showResponse(`POST /change-requests/${requestId}/reject`, {
        status: result.status,
        body: result.payload,
      });
      if (result.ok) {
        await refreshChangeRequests();
      }
    });
  });
}

function renderOpenQuestions(changeRequest, useModal = false) {
  changeRequestDetails.textContent =
    `Change Request #${changeRequest.id} | ${changeRequest.topic} | Status: ${changeRequest.status}`;
  const targetContainer = useModal ? questionsModalContent : openQuestionsContainer;
  targetContainer.innerHTML = "";
  if (useModal) {
    questionsModalMeta.textContent =
      `Change Request #${changeRequest.id} | ${changeRequest.topic} | Status: ${changeRequest.status}`;
  }

  if (!changeRequest.open_questions.length) {
    targetContainer.innerHTML =
      "<div class='text-muted'>No open questions were generated for this request.</div>";
    if (useModal) {
      questionsModal.show();
    }
    return;
  }

  for (const question of changeRequest.open_questions) {
    const wrapper = document.createElement("div");
    wrapper.className = "border rounded p-3 bg-light";
    const formDisabled = question.status === "answered";
    wrapper.innerHTML = `
      <div class="fw-semibold mb-2">Question #${question.id}</div>
      <div class="mb-2">${question.question_text}</div>
      <div class="small text-secondary mb-1"><strong>Why this matters:</strong> ${question.why_this_matters}</div>
      <div class="small text-secondary mb-2"><strong>Blocked areas:</strong> ${question.blocked_areas}</div>
      <div class="small mb-2"><strong>Status:</strong> ${question.status}</div>
      <div class="small mb-3"><strong>Current answer:</strong> ${question.answer_text || "pending"}</div>
      <form class="answerQuestionForm row g-2" data-question-id="${question.id}">
        <div class="col-12 col-md-4">
          <input class="form-control" name="answered_by" placeholder="Stakeholder name" ${formDisabled ? "disabled" : "required"} />
        </div>
        <div class="col-12 col-md-8">
          <input class="form-control" name="answer_text" placeholder="Answer" ${formDisabled ? "disabled" : "required"} />
        </div>
        <div class="col-12 d-grid">
          <button class="btn btn-sm btn-outline-success" type="submit" ${formDisabled ? "disabled" : ""}>Save Answer</button>
        </div>
      </form>
    `;
    targetContainer.appendChild(wrapper);
  }

  document.querySelectorAll(".answerQuestionForm").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const questionId = event.currentTarget.dataset.questionId;
      const result = await apiCall(`/open-questions/${questionId}/answer`, {
        method: "POST",
        body: JSON.stringify({
          answered_by: formData.get("answered_by"),
          answer_text: formData.get("answer_text"),
        }),
      });
      showResponse(`POST /open-questions/${questionId}/answer`, {
        status: result.status,
        body: result.payload,
      });
      if (result.ok) {
        await loadChangeRequest(changeRequest.id, useModal);
        await refreshChangeRequests();
      }
    });
  });

  if (useModal) {
    questionsModal.show();
  }
}

function renderPreview(preview) {
  previewModalContent.innerHTML = `
    <div class="mb-3">
      <strong>Files to change:</strong>
      <ul>${preview.files_to_change.map((item) => `<li>${item}</li>`).join("")}</ul>
    </div>
    <div class="mb-3">
      <strong>Tests to add/update:</strong>
      <ul>${preview.tests_to_update.map((item) => `<li>${item}</li>`).join("")}</ul>
    </div>
    <div class="mb-3">
      <strong>Docs to update:</strong>
      <ul>${preview.docs_to_update.map((item) => `<li>${item}</li>`).join("")}</ul>
    </div>
    <div class="mb-3">
      <strong>Conflict warnings:</strong>
      <ul>${preview.conflict_warnings.map((item) => `<li>${item}</li>`).join("")}</ul>
    </div>
    <div>
      <strong>Proposed diff preview:</strong>
      <pre class="response-box mt-2">${preview.diff_text}</pre>
    </div>
  `;
}

async function refreshChangeRequests() {
  const result = await apiCall("/change-requests");
  if (result.ok) {
    renderChangeRequests(result.payload);
  }
}

async function loadChangeRequest(id, useModal = false) {
  const result = await apiCall(`/change-requests/${id}`);
  showResponse(`GET /change-requests/${id}`, { status: result.status, body: result.payload });
  if (result.ok) {
    renderOpenQuestions(result.payload, useModal);
  }
}

document.getElementById("refreshEmployeesBtn").addEventListener("click", refreshEmployees);

changeRequestForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.currentTarget);
  const result = await apiCall("/change-requests", {
    method: "POST",
    body: JSON.stringify({
      request_date: form.get("request_date"),
      topic: form.get("topic"),
      request_summary: form.get("request_summary"),
    }),
  });
  showResponse("POST /change-requests", { status: result.status, body: result.payload });
  if (result.ok) {
    e.currentTarget.reset();
    setDefaultChangeRequestDate();
    renderOpenQuestions(result.payload);
    await refreshChangeRequests();
  }
});

document.getElementById("loadChangeRequestForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = new FormData(e.currentTarget).get("change_request_id");
  await loadChangeRequest(id);
});

finalApproveBtn.addEventListener("click", async () => {
  if (!activePreviewRequestId) {
    return;
  }
  const result = await apiCall(`/change-requests/${activePreviewRequestId}/approve`, { method: "POST" });
  showResponse(`POST /change-requests/${activePreviewRequestId}/approve`, {
    status: result.status,
    body: result.payload,
  });
  if (result.ok) {
    previewModal.hide();
    await refreshChangeRequests();
  }
});

setDefaultChangeRequestDate();

document.getElementById("createEmployeeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.currentTarget);
  const body = {
    full_name: form.get("full_name"),
    job_title: form.get("job_title"),
    country: form.get("country"),
    salary: Number(form.get("salary")),
  };

  const result = await apiCall("/employees", { method: "POST", body: JSON.stringify(body) });
  showResponse("POST /employees", { status: result.status, body: result.payload });
  if (result.ok) {
    e.currentTarget.reset();
    await refreshEmployees();
  }
});

document.getElementById("getEmployeeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = new FormData(e.currentTarget).get("employee_id");
  const result = await apiCall(`/employees/${id}`);
  showResponse(`GET /employees/${id}`, { status: result.status, body: result.payload });
});

document.getElementById("updateEmployeeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.currentTarget);
  const id = form.get("employee_id");
  const body = {};
  const fullName = form.get("full_name");
  const jobTitle = form.get("job_title");
  const country = form.get("country");
  const salary = form.get("salary");

  if (fullName) body.full_name = fullName;
  if (jobTitle) body.job_title = jobTitle;
  if (country) body.country = country;
  if (salary !== "") body.salary = Number(salary);

  const result = await apiCall(`/employees/${id}`, { method: "PUT", body: JSON.stringify(body) });
  showResponse(`PUT /employees/${id}`, { status: result.status, body: result.payload });
  if (result.ok) {
    await refreshEmployees();
  }
});

document.getElementById("deleteEmployeeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = new FormData(e.currentTarget).get("employee_id");
  const result = await apiCall(`/employees/${id}`, { method: "DELETE" });
  showResponse(`DELETE /employees/${id}`, { status: result.status, body: result.payload });
  if (result.ok) {
    e.currentTarget.reset();
    await refreshEmployees();
  }
});

document.getElementById("salaryCalcForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = new FormData(e.currentTarget).get("employee_id");
  const result = await apiCall(`/employees/${id}/salary/calculate`);
  showResponse(`GET /employees/${id}/salary/calculate`, { status: result.status, body: result.payload });
});

document.getElementById("countryMetricsForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const country = new FormData(e.currentTarget).get("country");
  const result = await apiCall(`/salary-metrics/country/${encodeURIComponent(country)}`);
  showResponse(`GET /salary-metrics/country/${country}`, { status: result.status, body: result.payload });
});

document.getElementById("jobTitleMetricsForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = new FormData(e.currentTarget).get("job_title");
  const result = await apiCall(`/salary-metrics/job-title/${encodeURIComponent(title)}`);
  showResponse(`GET /salary-metrics/job-title/${title}`, { status: result.status, body: result.payload });
});

refreshEmployees();
refreshChangeRequests();
