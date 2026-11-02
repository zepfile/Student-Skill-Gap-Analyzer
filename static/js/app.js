/**
 * Student Skill Gap Analyzer - Core Frontend Application Controller
 * Features: Day/Night Theme Mode, Live Gap Checklist Recalculation, ATS Score,
 * Interactive Skill Quizzes, Custom JD Analyzer, Markdown Report Export,
 * Confetti Celebrations, and Toast Notifications.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Global Chart instances
  let radarChartInstance = null;
  let doughnutChartInstance = null;

  // Cached active analysis state
  let currentAnalysisData = null;
  let activeStudentSkills = new Set();
  let originalStudentSkills = new Set();

  // Toast Notification Helper
  function showToast(message, isSuccess = true) {
    const toast = document.getElementById("toastNotification");
    const msgEl = document.getElementById("toastMessage");
    if (!toast || !msgEl) return;
    
    msgEl.textContent = message;
    const icon = toast.querySelector("i");
    if (icon) {
      icon.className = isSuccess ? "bi bi-check-circle-fill text-success fs-5" : "bi bi-exclamation-circle-fill text-warning fs-5";
    }
    
    toast.classList.remove("d-none");
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.classList.add("d-none");
    }, 3500);
  }

  // DOM Elements
  const form = document.getElementById("analyzerForm");
  const roleSelector = document.getElementById("roleSelector");
  const resumeFileInput = document.getElementById("resumeFileInput");
  const dropzone = document.getElementById("dropzone");
  const fileSelectedBadge = document.getElementById("fileSelectedBadge");
  const fileNameDisplay = document.getElementById("fileNameDisplay");
  const resumeTextArea = document.getElementById("resumeTextArea");
  const charCount = document.getElementById("charCount");
  const clearTextBtn = document.getElementById("clearTextBtn");
  const analyzeSubmitBtn = document.getElementById("analyzeSubmitBtn");
  const loadingState = document.getElementById("loadingState");
  const errorAlert = document.getElementById("errorAlert");
  const errorMessage = document.getElementById("errorMessage");
  const resultsDashboard = document.getElementById("resultsDashboard");
  const downloadReportBtn = document.getElementById("downloadReportBtn");
  const reAnalyzeBtn = document.getElementById("reAnalyzeBtn");

  // Snapshot elements
  const snapshotCategory = document.getElementById("snapshotCategory");
  const snapshotDemand = document.getElementById("snapshotDemand");
  const snapshotDesc = document.getElementById("snapshotDesc");
  const snapshotSalary = document.getElementById("snapshotSalary");
  const snapshotGrowth = document.getElementById("snapshotGrowth");

  // Sample Buttons
  const sampleBtns = document.querySelectorAll(".btn-sample");
  const quickSampleBtn = document.getElementById("quickSampleBtn");

  // Quiz Modal Elements
  const quizModalEl = document.getElementById("quizModal");
  const quizModal = quizModalEl ? new bootstrap.Modal(quizModalEl) : null;
  const quizSkillName = document.getElementById("quizSkillName");
  const quizModalBody = document.getElementById("quizModalBody");

  // Theme Toggle Elements
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const themeIcon = document.getElementById("themeIcon");
  const themeText = document.getElementById("themeText");

  let currentTheme = localStorage.getItem("skillgap_theme") || "dark";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("skillgap_theme", theme);

    if (themeIcon && themeText) {
      if (theme === "light") {
        themeIcon.className = "bi bi-sun-fill text-warning";
        themeText.textContent = "Day";
      } else {
        themeIcon.className = "bi bi-moon-stars-fill";
        themeText.textContent = "Night";
      }
    }

    if (currentAnalysisData) {
      renderRadarChart(currentAnalysisData.fit_analysis.radar_chart_data);
      renderDoughnutChart(currentAnalysisData.fit_analysis);
    }
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      currentTheme = currentTheme === "dark" ? "light" : "dark";
      applyTheme(currentTheme);
      showToast(`Switched to ${currentTheme === "dark" ? "Night" : "Day"} mode`);
    });
  }

  // Initialize theme on load
  applyTheme(currentTheme);

  // 1. Role Change Handler
  function updateRoleSnapshot() {
    if (!roleSelector) return;
    const selectedOption = roleSelector.options[roleSelector.selectedIndex];
    if (!selectedOption) return;

    if (snapshotCategory) {
      snapshotCategory.textContent = selectedOption.getAttribute("data-category") || "General";
    }
    if (snapshotDemand) {
      snapshotDemand.innerHTML = `<i class="bi bi-fire me-1"></i> ${selectedOption.getAttribute("data-demand") || "9.0"}/10`;
    }
    if (snapshotSalary) {
      snapshotSalary.textContent = selectedOption.getAttribute("data-salary") || "Competitive";
    }
    if (snapshotGrowth) {
      snapshotGrowth.innerHTML = `<i class="bi bi-graph-up-arrow me-1"></i> ${selectedOption.getAttribute("data-growth") || "+24% YoY"}`;
    }
    if (snapshotDesc) {
      snapshotDesc.textContent = selectedOption.getAttribute("data-description") || "Designs, builds, and maintains software solutions.";
    }
  }

  if (roleSelector) {
    roleSelector.addEventListener("change", updateRoleSnapshot);
    updateRoleSnapshot();
  }

  // 2. Character counter & Text input
  if (resumeTextArea && charCount) {
    resumeTextArea.addEventListener("input", () => {
      const len = resumeTextArea.value.length;
      charCount.textContent = `${len.toLocaleString()} characters`;
    });
  }

  if (clearTextBtn && resumeTextArea) {
    clearTextBtn.addEventListener("click", () => {
      resumeTextArea.value = "";
      if (charCount) charCount.textContent = "0 characters";
      showToast("Resume text cleared", false);
    });
  }

  // 3. File Input & Drag/Drop Handling
  if (resumeFileInput) {
    resumeFileInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        if (fileNameDisplay) fileNameDisplay.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        if (fileSelectedBadge) fileSelectedBadge.classList.remove("d-none");
        showToast(`Loaded file: ${file.name}`);
      } else {
        if (fileSelectedBadge) fileSelectedBadge.classList.add("d-none");
      }
    });
  }

  if (dropzone) {
    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "#6366f1";
    });

    dropzone.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "";
    });

    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.style.borderColor = "";
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        resumeFileInput.files = e.dataTransfer.files;
        const file = e.dataTransfer.files[0];
        if (fileNameDisplay) fileNameDisplay.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        if (fileSelectedBadge) fileSelectedBadge.classList.remove("d-none");
        showToast(`Loaded file: ${file.name}`);
      }
    });
  }

  // 4. Sample Resume Loading
  async function loadSample(sampleType) {
    try {
      const res = await fetch(`/api/sample-resume/${sampleType}`);
      const data = await res.json();
      if (data.success && resumeTextArea) {
        const pasteTabBtn = document.getElementById("tab-paste");
        if (pasteTabBtn) {
          const tabTrigger = new bootstrap.Tab(pasteTabBtn);
          tabTrigger.show();
        }

        resumeTextArea.value = data.sample_text;
        if (charCount) charCount.textContent = `${data.sample_text.length.toLocaleString()} characters`;

        if (sampleType === "python_developer" || sampleType === "1") {
          roleSelector.value = "1";
        } else if (sampleType === "data_analyst" || sampleType === "4") {
          roleSelector.value = "4";
        } else if (sampleType === "web_developer" || sampleType === "3") {
          roleSelector.value = "3";
        }

        updateRoleSnapshot();
        form.scrollIntoView({ behavior: "smooth" });
        showToast(`Loaded sample candidate profile!`);
      }
    } catch (err) {
      console.error("Failed to load sample resume:", err);
    }
  }

  sampleBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const type = btn.getAttribute("data-sample");
      loadSample(type);
    });
  });

  if (quickSampleBtn) {
    quickSampleBtn.addEventListener("click", () => {
      loadSample("python_developer");
    });
  }

  // 5. Form Submit - Run Analysis
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const hasFile = resumeFileInput.files && resumeFileInput.files.length > 0;
      const hasText = resumeTextArea.value.trim().length > 0;

      if (!hasFile && !hasText) {
        showError("Please upload a resume file (PDF/DOCX) or paste your resume content in the text box.");
        return;
      }

      hideError();
      showLoading(true);

      const formData = new FormData(form);

      try {
        const response = await fetch("/api/analyze", {
          method: "POST",
          body: formData,
        });

        const result = await response.json();
        showLoading(false);

        if (!result.success) {
          showError(result.error || "Analysis failed. Please check your inputs.");
          return;
        }

        currentAnalysisData = result;

        // Initialize active skills set for dynamic interactive recalculation
        activeStudentSkills = new Set(result.candidate_profile.extracted_skills.map((s) => s.name));
        originalStudentSkills = new Set(activeStudentSkills);

        renderResults(result);

        if (resultsDashboard) {
          resultsDashboard.classList.remove("d-none");
          resultsDashboard.scrollIntoView({ behavior: "smooth" });
        }

        showToast("Analysis complete! Review your career readiness report.");
      } catch (err) {
        showLoading(false);
        showError("A network error occurred while communicating with the server: " + err.message);
      }
    });
  }

  if (reAnalyzeBtn) {
    reAnalyzeBtn.addEventListener("click", () => {
      const inputCard = document.getElementById("inputCard");
      if (inputCard) inputCard.scrollIntoView({ behavior: "smooth" });
    });
  }

  // 6. Download Assessment Report (.md)
  if (downloadReportBtn) {
    downloadReportBtn.addEventListener("click", async () => {
      if (!currentAnalysisData) return;

      downloadReportBtn.disabled = true;
      downloadReportBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Preparing Report...`;

      try {
        const res = await fetch("/api/export-report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(currentAnalysisData),
        });

        if (res.ok) {
          const blob = await res.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.style.display = "none";
          a.href = url;
          a.download = `SkillGap_Assessment_${currentAnalysisData.fit_analysis.role_id}.md`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          a.remove();
          showToast("Assessment report (.md) downloaded successfully!");
        } else {
          alert("Failed to export markdown report.");
        }
      } catch (err) {
        alert("Error exporting report: " + err.message);
      } finally {
        downloadReportBtn.disabled = false;
        downloadReportBtn.innerHTML = `<i class="bi bi-file-earmark-arrow-down me-1"></i> Export Report (.md)`;
      }
    });
  }

  // 7. Render All Results
  function renderResults(data) {
    const { candidate_profile, fit_analysis, roadmap, role_comparisons, ats_feedback } = data;

    // Header & Titles
    const titleEl = document.getElementById("resultRoleTitle");
    if (titleEl) titleEl.textContent = fit_analysis.role_title;

    const subEl = document.getElementById("resultSubtitle");
    if (subEl) subEl.textContent = fit_analysis.role_description;

    // Top Metric Cards
    updateReadinessScoreDisplay(fit_analysis.readiness_score, fit_analysis.readiness_level, fit_analysis.readiness_badge);

    // ATS Compatibility Score
    if (ats_feedback) {
      const atsVal = document.getElementById("atsScoreVal");
      if (atsVal) atsVal.textContent = Math.round(ats_feedback.overall_score);

      const atsBadge = document.getElementById("atsBadge");
      if (atsBadge) {
        atsBadge.textContent = ats_feedback.tier;
        atsBadge.className = `badge bg-${ats_feedback.tier_badge}-subtle text-${ats_feedback.tier_badge}`;
      }

      const atsSummary = document.getElementById("atsVerbsSummary");
      if (atsSummary) {
        atsSummary.innerHTML = `<i class="bi bi-check-all text-success me-1"></i> ${ats_feedback.action_verb_count} Action Verbs Identified`;
      }
    }

    // Core Gaps
    const missingCoreEl = document.getElementById("missingCoreCount");
    if (missingCoreEl) missingCoreEl.textContent = fit_analysis.missing_core.length;

    const totalCore = fit_analysis.matched_core.length + fit_analysis.missing_core.length;
    const coverageEl = document.getElementById("coreCoverageRatio");
    if (coverageEl) coverageEl.textContent = `${fit_analysis.matched_core.length} of ${totalCore} core competencies matched`;

    // Estimated Roadmap
    const estWeeksEl = document.getElementById("estWeeksVal");
    if (estWeeksEl) estWeeksEl.textContent = `${roadmap.estimated_weeks} Weeks`;

    // NLP Cosine & Contact
    const nlpEl = document.getElementById("nlpSimVal");
    if (nlpEl) nlpEl.textContent = `${fit_analysis.nlp_similarity}%`;

    const emailDisp = (candidate_profile.contact_info && candidate_profile.contact_info.email) ? candidate_profile.contact_info.email : "Verified in Profile";
    const emailEl = document.getElementById("contactEmailDisplay");
    if (emailEl) emailEl.textContent = emailDisp;

    // Salary & Market Intelligence
    if (fit_analysis.salary_percentiles) {
      const p25 = document.getElementById("salaryP25");
      if (p25) p25.textContent = fit_analysis.salary_percentiles.p25 || "₹6 LPA";
      const pMed = document.getElementById("salaryMedian");
      if (pMed) pMed.textContent = fit_analysis.salary_percentiles.median || "₹12 LPA";
      const p90 = document.getElementById("salaryP90");
      if (p90) p90.textContent = fit_analysis.salary_percentiles.p90 || "₹22 LPA";
    }

    if (fit_analysis.growth_rate) {
      const growthEl = document.getElementById("marketGrowthDisplay");
      if (growthEl) growthEl.textContent = fit_analysis.growth_rate;
    }

    if (fit_analysis.market_demand) {
      const demandEl = document.getElementById("marketDemandRating");
      if (demandEl) demandEl.textContent = `Rating: ${fit_analysis.market_demand} / 10`;
    }

    if (fit_analysis.top_industries) {
      const indPills = document.getElementById("topIndustriesPills");
      if (indPills) {
        indPills.innerHTML = fit_analysis.top_industries
          .map((ind) => `<span class="badge bg-dark border border-secondary text-secondary">${ind}</span>`)
          .join("");
      }
    }

    // Render Charts
    renderRadarChart(fit_analysis.radar_chart_data);
    renderDoughnutChart(fit_analysis);

    // Render Tabs
    renderGapCards(fit_analysis.gap_items);
    renderATSFeedback(ats_feedback);
    renderRoadmap(roadmap);
    renderStrengths(fit_analysis);
    renderAllRolesTable(role_comparisons);
  }

  function updateReadinessScoreDisplay(score, level, badgeColor) {
    const scoreVal = document.getElementById("readinessScoreVal");
    if (scoreVal) scoreVal.textContent = `${score}%`;

    const readinessBadge = document.getElementById("readinessBadge");
    if (readinessBadge) {
      readinessBadge.textContent = level;
      readinessBadge.className = `badge bg-${badgeColor}-subtle text-${badgeColor} border border-${badgeColor}-subtle`;
    }

    const progressBar = document.getElementById("readinessProgressBar");
    if (progressBar) {
      progressBar.style.width = `${score}%`;
      if (score < 50) {
        progressBar.style.background = "#ef4444";
      } else if (score < 75) {
        progressBar.style.background = "#f59e0b";
      } else {
        progressBar.style.background = "linear-gradient(90deg, #6366f1, #10b981)";
      }
    }
  }

  // Chart 1: Radar Chart
  function renderRadarChart(radarData) {
    const canvas = document.getElementById("radarChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    if (radarChartInstance) {
      radarChartInstance.destroy();
    }

    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    const gridColor = isLight ? "rgba(0, 0, 0, 0.08)" : "rgba(255, 255, 255, 0.08)";
    const labelColor = isLight ? "#1e293b" : "#cbd5e1";
    const legendColor = isLight ? "#0f172a" : "#e2e8f0";

    radarChartInstance = new Chart(ctx, {
      type: "radar",
      data: {
        labels: radarData.labels,
        datasets: [
          {
            label: "Your Candidate Profile",
            data: radarData.student_values,
            backgroundColor: "rgba(99, 102, 241, 0.25)",
            borderColor: "#6366f1",
            pointBackgroundColor: "#6366f1",
            pointBorderColor: "#fff",
            borderWidth: 2,
          },
          {
            label: "Target Role Benchmark (100%)",
            data: radarData.benchmark_values,
            backgroundColor: "rgba(16, 185, 129, 0.08)",
            borderColor: "rgba(16, 185, 129, 0.6)",
            borderDash: [4, 4],
            pointBackgroundColor: "#10b981",
            borderWidth: 1.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: gridColor },
            grid: { color: gridColor },
            pointLabels: { color: labelColor, font: { size: 11, weight: "bold" } },
            ticks: { display: false, maxTicksLimit: 5 },
            suggestedMin: 0,
            suggestedMax: 100,
          },
        },
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: legendColor, boxWidth: 12, padding: 12, font: { size: 11 } },
          },
        },
      },
    });
  }

  // Chart 2: Doughnut Chart
  function renderDoughnutChart(fit) {
    const canvas = document.getElementById("doughnutChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    if (doughnutChartInstance) {
      doughnutChartInstance.destroy();
    }

    const isLight = document.documentElement.getAttribute("data-theme") === "light";
    const legendColor = isLight ? "#0f172a" : "#e2e8f0";
    const borderColor = isLight ? "#ffffff" : "#111827";

    doughnutChartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Verified Core", "Verified Secondary", "Missing Core", "Missing Secondary"],
        datasets: [
          {
            data: [
              fit.matched_core.length,
              fit.matched_secondary.length,
              fit.missing_core.length,
              fit.missing_secondary.length,
            ],
            backgroundColor: [
              "#10b981", // green: matched core
              "#6366f1", // purple: matched secondary
              "#ef4444", // red: missing core
              "#f59e0b", // yellow: missing secondary
            ],
            borderWidth: 2,
            borderColor: borderColor,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: legendColor, boxWidth: 12, padding: 12, font: { size: 11 } },
          },
        },
        cutout: "68%",
      },
    });
  }

  // Render Gap Cards with Interactive "Mark as Learned" Checkbox & Diagnostic Quiz Button
  function renderGapCards(gapItems) {
    const container = document.getElementById("gapCardsContainer");
    if (!container) return;
    container.innerHTML = "";

    if (!gapItems || gapItems.length === 0) {
      container.innerHTML = `
        <div class="col-12 text-center py-5">
          <div class="text-success display-4 mb-2"><i class="bi bi-patch-check-fill"></i></div>
          <h5 class="fw-bold">Outstanding! No Critical Skill Gaps Detected!</h5>
          <p class="text-muted">You meet all core and secondary competencies for this role.</p>
        </div>
      `;
      return;
    }

    gapItems.forEach((item) => {
      const isHigh = item.priority_code === "high";
      const badgeClass = isHigh ? "badge-priority-high" : "badge-priority-medium";

      let resourcesHtml = "";
      if (item.resources && item.resources.length > 0) {
        resourcesHtml = item.resources
          .map(
            (r) => `
          <a href="${r.url}" target="_blank" rel="noopener noreferrer" class="badge bg-dark border border-secondary text-light text-decoration-none p-2 mb-1 me-1 d-inline-flex align-items-center">
            <i class="bi bi-box-arrow-up-right me-1 text-primary"></i> ${r.title} <span class="badge bg-secondary ms-2">${r.type || "Online"}</span>
          </a>
        `
          )
          .join("");
      }

      let projectsHtml = "";
      if (item.project_ideas && item.project_ideas.length > 0) {
        projectsHtml = item.project_ideas
          .map((p) => `<li class="small text-muted"><i class="bi bi-arrow-right text-info me-1"></i>${p}</li>`)
          .join("");
      }

      const card = document.createElement("div");
      card.className = "col-md-6";
      card.id = `gap-card-${item.skill.replace(/[^a-zA-Z0-9]/g, "_")}`;
      card.innerHTML = `
        <div class="gap-card ${!isHigh ? "medium-priority" : ""}">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <div>
              <div class="d-flex align-items-center gap-2">
                <h5 class="fw-bold mb-0 text-light">${item.skill}</h5>
                <span class="${badgeClass}">${item.priority}</span>
              </div>
              <span class="small text-muted">${item.category}</span>
            </div>
            <!-- Interactive Diagnostic Quiz Button -->
            <button class="btn btn-sm btn-take-quiz" data-skill="${item.skill}">
              <i class="bi bi-mortarboard-fill me-1"></i> Test Yourself
            </button>
          </div>

          <!-- Mark As Acquired Checkbox (Live recalculation) -->
          <div class="form-check form-switch my-2 p-2 rounded bg-dark border border-secondary-subtle">
            <input class="form-check-input ms-0 me-2 skill-learned-check" type="checkbox" id="check-${item.skill}" data-skill="${item.skill}" data-importance="${item.importance}">
            <label class="form-check-label small fw-semibold text-light cursor-pointer" for="check-${item.skill}">
              I already know this skill / Mark as Learned
            </label>
          </div>

          <div class="mt-2">
            <div class="small fw-semibold text-secondary mb-1"><i class="bi bi-book me-1"></i> Recommended Learning Path:</div>
            <div class="d-flex flex-wrap">${resourcesHtml}</div>
          </div>

          ${
            projectsHtml
              ? `
          <div class="mt-3 pt-2 border-top border-secondary-subtle">
            <div class="small fw-semibold text-secondary mb-1"><i class="bi bi-hammer me-1"></i> Portfolio Project:</div>
            <ul class="list-unstyled mb-0">${projectsHtml}</ul>
          </div>
          `
              : ""
          }
        </div>
      `;
      container.appendChild(card);
    });

    // Wire up interactive "Mark as Learned" live score updates
    document.querySelectorAll(".skill-learned-check").forEach((chk) => {
      chk.addEventListener("change", (e) => {
        handleSkillCheckToggle(e.target.getAttribute("data-skill"), e.target.checked);
      });
    });

    // Wire up Quiz Buttons
    document.querySelectorAll(".btn-take-quiz").forEach((btn) => {
      btn.addEventListener("click", () => {
        openQuizModal(btn.getAttribute("data-skill"));
      });
    });
  }

  // 8. Live Interactive Skill Check-off Recalculation Engine
  function handleSkillCheckToggle(skillName, isChecked) {
    if (!currentAnalysisData) return;

    const fit = currentAnalysisData.fit_analysis;
    const cardEl = document.getElementById(`gap-card-${skillName.replace(/[^a-zA-Z0-9]/g, "_")}`);

    if (isChecked) {
      activeStudentSkills.add(skillName);
      if (cardEl) {
        const gapCardInner = cardEl.querySelector(".gap-card");
        if (gapCardInner) gapCardInner.classList.add("acquired");
      }
      showToast(`Skill "${skillName}" marked as learned! Score updated.`);
    } else {
      activeStudentSkills.delete(skillName);
      if (cardEl) {
        const gapCardInner = cardEl.querySelector(".gap-card");
        if (gapCardInner) gapCardInner.classList.remove("acquired");
      }
    }

    // Recalculate match metrics
    const coreReq = new Set(fit.matched_core.concat(fit.missing_core));
    const secReq = new Set(fit.matched_secondary.concat(fit.missing_secondary));

    const updatedMatchedCore = Array.from(coreReq).filter((s) => activeStudentSkills.has(s));
    const updatedMissingCore = Array.from(coreReq).filter((s) => !activeStudentSkills.has(s));

    const updatedMatchedSec = Array.from(secReq).filter((s) => activeStudentSkills.has(s));
    const updatedMissingSec = Array.from(secReq).filter((s) => !activeStudentSkills.has(s));

    const totalPoints = coreReq.size * 2.0 + secReq.size * 1.0;
    const earnedPoints = updatedMatchedCore.length * 2.0 + updatedMatchedSec.length * 1.0;
    const skillPct = totalPoints > 0 ? (earnedPoints / totalPoints) * 100.0 : 0;
    const nlpSim = fit.nlp_similarity || 70.0;
    const updatedReadiness = Math.min(100.0, Math.round(skillPct * 0.75 + nlpSim * 0.25));

    let level = "Developing (Noticeable Gaps)";
    let badge = "warning";
    if (updatedReadiness >= 80) {
      level = "Job Ready (High Match)";
      badge = "success";
    } else if (updatedReadiness >= 60) {
      level = "Intermediate (Moderate Gaps)";
      badge = "primary";
    }

    // Update Top Score Display
    updateReadinessScoreDisplay(updatedReadiness, level, badge);
    const missingCountEl = document.getElementById("missingCoreCount");
    if (missingCountEl) missingCountEl.textContent = updatedMissingCore.length;

    const ratioEl = document.getElementById("coreCoverageRatio");
    if (ratioEl) ratioEl.textContent = `${updatedMatchedCore.length} of ${coreReq.size} core competencies verified`;

    // Update Doughnut Chart Live
    if (doughnutChartInstance) {
      doughnutChartInstance.data.datasets[0].data = [
        updatedMatchedCore.length,
        updatedMatchedSec.length,
        updatedMissingCore.length,
        updatedMissingSec.length,
      ];
      doughnutChartInstance.update();
    }
  }

  // 9. Interactive Skill Diagnostic Quiz Engine
  async function openQuizModal(skillName) {
    if (!quizModal) return;
    if (quizSkillName) quizSkillName.textContent = skillName;
    if (quizModalBody) {
      quizModalBody.innerHTML = `
        <div class="text-center py-4">
          <div class="spinner-border text-primary" role="status"></div>
          <div class="mt-2 text-muted small">Loading diagnostic questions for ${skillName}...</div>
        </div>
      `;
    }
    quizModal.show();

    try {
      const res = await fetch(`/api/skill-quiz/${encodeURIComponent(skillName)}`);
      const data = await res.json();

      if (data.success && data.quiz && data.quiz.questions) {
        renderQuizQuestions(data.quiz.questions, skillName);
      } else {
        if (quizModalBody) quizModalBody.innerHTML = `<div class="alert alert-warning">No quiz questions available for ${skillName} at this time.</div>`;
      }
    } catch (err) {
      if (quizModalBody) quizModalBody.innerHTML = `<div class="alert alert-danger">Error loading quiz: ${err.message}</div>`;
    }
  }

  function renderQuizQuestions(questions, skillName) {
    if (!quizModalBody) return;
    let score = 0;
    let answered = 0;

    quizModalBody.innerHTML = `
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="small text-muted">Test your core knowledge of <strong>${skillName}</strong>:</div>
        <span class="badge bg-primary-subtle text-primary" id="quizScoreTracker">Score: 0 / ${questions.length}</span>
      </div>
      <div id="quizQuestionsContainer"></div>
    `;

    const container = document.getElementById("quizQuestionsContainer");
    if (!container) return;

    questions.forEach((q, qIdx) => {
      const card = document.createElement("div");
      card.className = "quiz-card";
      card.innerHTML = `
        <div class="fw-bold mb-2 text-light"><span class="badge bg-secondary me-2">Q${qIdx + 1}</span> ${q.question}</div>
        <div class="quiz-options">
          ${q.options
            .map(
              (opt, optIdx) => `
            <button class="quiz-option-btn" data-qidx="${qIdx}" data-optidx="${optIdx}">
              ${opt}
            </button>
          `
            )
            .join("")}
        </div>
        <div class="quiz-explanation d-none" id="quiz-exp-${qIdx}">
          <i class="bi bi-info-circle me-1 text-primary"></i> ${q.explanation}
        </div>
      `;
      container.appendChild(card);
    });

    // Wire up option clicks
    container.querySelectorAll(".quiz-option-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const qIdx = parseInt(btn.getAttribute("data-qidx"));
        const optIdx = parseInt(btn.getAttribute("data-optidx"));
        const parent = btn.closest(".quiz-options");

        if (parent.getAttribute("data-answered") === "true") return;
        parent.setAttribute("data-answered", "true");

        const correctIdx = questions[qIdx].correct_index;
        const explanationEl = document.getElementById(`quiz-exp-${qIdx}`);
        if (explanationEl) explanationEl.classList.remove("d-none");

        if (optIdx === correctIdx) {
          btn.classList.add("correct");
          score++;
        } else {
          btn.classList.add("incorrect");
          const allBtns = parent.querySelectorAll(".quiz-option-btn");
          if (allBtns[correctIdx]) allBtns[correctIdx].classList.add("correct");
        }

        answered++;
        const tracker = document.getElementById("quizScoreTracker");
        if (tracker) tracker.textContent = `Score: ${score} / ${questions.length}`;

        if (answered === questions.length) {
          // Trigger celebration confetti if passed with 2 or 3 correct answers
          if (score >= 2 && typeof confetti === "function") {
            try {
              confetti({
                particleCount: 90,
                spread: 70,
                origin: { y: 0.6 }
              });
            } catch (e) {
              // Ignore confetti error
            }
          }

          const summary = document.createElement("div");
          summary.className = "alert alert-success mt-3 text-center";
          summary.innerHTML = `
            <div class="h5 fw-bold mb-1">Diagnostic Completed! Final Score: ${score} / ${questions.length}</div>
            <div class="small">${score >= 2 ? "🎉 Awesome job! You have solid foundational knowledge." : "Keep learning! Follow the recommended courses in your roadmap."}</div>
          `;
          container.appendChild(summary);
        }
      });
    });
  }

  // 10. Render ATS Health & Action Verbs
  function renderATSFeedback(ats) {
    if (!ats) return;

    const secEl = document.getElementById("atsSubSections");
    if (secEl) secEl.textContent = `${ats.subscores.sections} / 30`;

    const secDet = document.getElementById("atsSectionsDetail");
    if (secDet) secDet.textContent = `${ats.present_sections.length} of 5 sections present`;

    const verbSub = document.getElementById("atsSubVerbs");
    if (verbSub) verbSub.textContent = `${ats.subscores.action_verbs} / 25`;

    const verbCnt = document.getElementById("atsVerbsCount");
    if (verbCnt) verbCnt.textContent = `${ats.action_verb_count} high-impact verbs`;

    const impSub = document.getElementById("atsSubImpact");
    if (impSub) impSub.textContent = `${ats.subscores.quantifiable_impact} / 25`;

    const impMet = document.getElementById("atsMetricsCount");
    if (impMet) impMet.textContent = `${ats.metrics_detected} metrics / % detected`;

    const lenSub = document.getElementById("atsSubLength");
    if (lenSub) lenSub.textContent = `${ats.subscores.length_format} / 20`;

    const lenWord = document.getElementById("atsWordCount");
    if (lenWord) lenWord.textContent = `${ats.word_count} total words`;

    // Action Verbs Pills
    const verbsContainer = document.getElementById("atsActionVerbsPills");
    if (verbsContainer) {
      verbsContainer.innerHTML = ats.action_verbs_found.length
        ? ats.action_verbs_found.map((v) => `<span class="badge bg-success-subtle text-success p-2"><i class="bi bi-lightning-charge-fill me-1"></i>${v}</span>`).join("")
        : '<span class="text-muted small">No prominent action verbs identified. Consider beginning bullets with words like "Engineered", "Optimized", "Architected".</span>';
    }

    // Weak / Passive Phrases Audit Container
    const weakCountBadge = document.getElementById("atsWeakPhrasesCountBadge");
    const weakContainer = document.getElementById("atsWeakPhrasesContainer");
    if (weakContainer) {
      const weakList = ats.weak_phrases_detected || [];
      if (weakCountBadge) {
        weakCountBadge.textContent = `${weakList.length} detected`;
        weakCountBadge.className = weakList.length > 0 ? "badge bg-warning-subtle text-warning" : "badge bg-success-subtle text-success";
      }

      if (weakList.length === 0) {
        weakContainer.innerHTML = `
          <div class="col-12">
            <div class="p-3 rounded-3 bg-success-subtle text-success small d-flex align-items-center gap-2">
              <i class="bi bi-patch-check-fill fs-5"></i>
              <span><strong>Excellent action orientation!</strong> No passive phrases detected in your uploaded resume. You already maintain strong engineering ownership words.</span>
            </div>
          </div>
        `;
      } else {
        weakContainer.innerHTML = weakList.map((item, idx) => `
          <div class="col-md-6">
            <div class="p-3 rounded-3 bg-dark-subtle border h-100">
              <div class="d-flex justify-content-between align-items-center mb-1">
                <span class="badge bg-danger-subtle text-danger"><i class="bi bi-x-circle me-1"></i>"${item.weak_phrase}"</span>
                <span class="small text-muted" style="font-size: 0.75rem;">Passive Verb</span>
              </div>
              <div class="small text-muted mb-2 font-monospace" style="font-size: 0.8rem;">
                Line: "${item.original_line}"
              </div>
              <div class="p-2 rounded bg-dark border border-success-subtle mb-2">
                <div class="small fw-bold text-success mb-1"><i class="bi bi-arrow-right-circle-fill me-1"></i>Enhanced Preview:</div>
                <div class="small text-light font-monospace" id="enhanced-weak-text-${idx}">
                  ${item.enhanced_preview}
                </div>
              </div>
              <div class="d-flex justify-content-between align-items-center">
                <div class="small text-muted" style="font-size: 0.75rem;">
                  Try: <strong>${item.power_replacements.slice(0, 3).join(", ")}</strong>
                </div>
                <button type="button" class="btn btn-sm btn-outline-success py-0 px-2 btn-copy-enhanced" data-target="enhanced-weak-text-${idx}">
                  <i class="bi bi-clipboard me-1"></i> Copy
                </button>
              </div>
            </div>
          </div>
        `).join("");

        // Wire up copy buttons
        weakContainer.querySelectorAll(".btn-copy-enhanced").forEach((btn) => {
          btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const textToCopy = document.getElementById(targetId).textContent.trim();
            navigator.clipboard.writeText(textToCopy);
            btn.innerHTML = `<i class="bi bi-check2 text-success me-1"></i> Copied!`;
            showToast("Copied enhanced bullet to clipboard!");
            setTimeout(() => {
              btn.innerHTML = `<i class="bi bi-clipboard me-1"></i> Copy`;
            }, 2000);
          });
        });
      }
    }

    // Power Verbs Taxonomy by Category
    const powerCatContainer = document.getElementById("atsPowerVerbCategoriesContainer");
    if (powerCatContainer && ats.power_verb_categories) {
      powerCatContainer.innerHTML = Object.entries(ats.power_verb_categories).map(([catName, verbs]) => `
        <div class="col-md-6 col-lg-3">
          <div class="p-3 rounded-3 bg-dark-subtle border h-100">
            <div class="small fw-bold text-light text-uppercase mb-2">${catName}</div>
            <div class="d-flex flex-wrap gap-1">
              ${verbs.map((v) => `
                <span class="badge bg-secondary-subtle text-light p-1" title="${v.example}" style="cursor: help; font-size: 0.78rem;">
                  ${v.verb}
                </span>
              `).join("")}
            </div>
          </div>
        </div>
      `).join("");
    }

    // Suggestions List
    const suggContainer = document.getElementById("atsSuggestionsList");
    if (suggContainer) {
      suggContainer.innerHTML = ats.suggestions.map((s) => `<li class="mb-2">${s}</li>`).join("");
    }
  }

  // 11. Render Roadmap Timeline & Interview Prep
  function renderRoadmap(roadmap) {
    const timeline = document.getElementById("roadmapTimeline");
    if (!timeline) return;
    timeline.innerHTML = "";

    roadmap.phases.forEach((phase) => {
      const card = document.createElement("div");
      card.className = "timeline-item";

      let skillsHtml = "";
      if (phase.skills && phase.skills.length > 0) {
        skillsHtml = `
          <div class="row g-2 mt-2">
            ${phase.skills
              .map(
                (s) => `
              <div class="col-md-6">
                <div class="p-2 rounded bg-dark border border-secondary small">
                  <div class="fw-bold text-info">${s.skill}</div>
                  <div class="text-muted" style="font-size: 0.8rem;">${s.action_item}</div>
                </div>
              </div>
            `
              )
              .join("")}
          </div>
        `;
      }

      let projectHtml = "";
      if (phase.project_name) {
        projectHtml = `
          <div class="p-3 mt-2 rounded bg-dark border border-primary-subtle">
            <div class="fw-bold text-primary mb-1"><i class="bi bi-star-fill text-warning me-1"></i> ${phase.project_name}</div>
            <div class="small text-muted mb-2">${phase.project_description}</div>
            <div class="small text-secondary fw-semibold">Key Deliverables:</div>
            <ul class="mb-0 ps-3 small text-muted">
              ${phase.deliverables.map((d) => `<li>${d}</li>`).join("")}
            </ul>
          </div>
        `;
      }

      card.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-card">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <h6 class="fw-bold mb-0 text-light">${phase.title}</h6>
            <span class="badge bg-primary-subtle text-primary">${phase.duration}</span>
          </div>
          <p class="small text-muted mb-2">${phase.focus}</p>
          ${skillsHtml}
          ${projectHtml}
        </div>
      `;
      timeline.appendChild(card);
    });

    // Technical Interview Prep Accordion
    const accordion = document.getElementById("interviewQuestionsAccordion");
    if (accordion && roadmap.interview_questions && roadmap.interview_questions.length > 0) {
      accordion.innerHTML = "";
      roadmap.interview_questions.forEach((q, idx) => {
        const item = document.createElement("div");
        item.className = "accordion-item";
        item.innerHTML = `
          <h2 class="accordion-header" id="heading${idx}">
            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${idx}">
              <span class="badge bg-secondary me-2">Q${idx + 1}</span> ${q.question}
            </button>
          </h2>
          <div id="collapse${idx}" class="accordion-collapse collapse" data-bs-parent="#interviewQuestionsAccordion">
            <div class="accordion-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="small fw-bold text-warning"><i class="bi bi-key-fill me-1"></i> Expected Answer Framework:</div>
                <button type="button" class="btn btn-sm btn-outline-secondary btn-copy-qa py-0 px-2" data-question="${q.question.replace(/"/g, '&quot;')}" data-answer="${q.key_points.replace(/"/g, '&quot;')}">
                  <i class="bi bi-clipboard me-1"></i> Copy Answer
                </button>
              </div>
              <div>${q.key_points}</div>
            </div>
          </div>
        `;
        accordion.appendChild(item);
      });

      // Wire up copy answer buttons
      accordion.querySelectorAll(".btn-copy-qa").forEach((btn) => {
        btn.addEventListener("click", () => {
          const qText = btn.getAttribute("data-question");
          const aText = btn.getAttribute("data-answer");
          navigator.clipboard.writeText(`Q: ${qText}\n\nAnswer Framework:\n${aText}`);
          btn.innerHTML = `<i class="bi bi-check2 text-success me-1"></i> Copied!`;
          showToast("Interview answer framework copied to clipboard!");
          setTimeout(() => {
            btn.innerHTML = `<i class="bi bi-clipboard me-1"></i> Copy Answer`;
          }, 2000);
        });
      });
    }
  }

  // 12. Render Strengths & Bonus Skills
  function renderStrengths(fit) {
    const coreContainer = document.getElementById("matchedCorePills");
    if (coreContainer) {
      coreContainer.innerHTML = fit.matched_core.length
        ? fit.matched_core
            .map((s) => `<span class="badge bg-success-subtle text-success border border-success-subtle p-2 m-1 fs-6"><i class="bi bi-check-circle-fill me-1"></i> ${s}</span>`)
            .join("")
        : '<span class="text-muted small">No core matches found.</span>';
    }

    const secContainer = document.getElementById("matchedSecondaryPills");
    if (secContainer) {
      secContainer.innerHTML = fit.matched_secondary.length
        ? fit.matched_secondary
            .map((s) => `<span class="badge bg-primary-subtle text-primary border border-primary-subtle p-2 m-1 fs-6"><i class="bi bi-check2 me-1"></i> ${s}</span>`)
            .join("")
        : '<span class="text-muted small">No secondary matches found.</span>';
    }

    const softContainer = document.getElementById("matchedSoftPills");
    if (softContainer) {
      softContainer.innerHTML = fit.matched_soft.length
        ? fit.matched_soft
            .map((s) => `<span class="badge bg-info-subtle text-info border border-info-subtle p-2 m-1 fs-6"><i class="bi bi-person-check me-1"></i> ${s}</span>`)
            .join("")
        : '<span class="text-muted small">No soft skill matches explicitly mentioned.</span>';
    }

    const bonusContainer = document.getElementById("bonusSkillsPills");
    if (bonusContainer) {
      bonusContainer.innerHTML = fit.bonus_skills.length
        ? fit.bonus_skills
            .map((s) => `<span class="badge bg-warning-subtle text-warning border border-warning-subtle p-2 m-1 fs-6"><i class="bi bi-stars me-1"></i> ${s}</span>`)
            .join("")
        : '<span class="text-muted small">No extra skills detected.</span>';
    }
  }

  // 13. Render Multi-Role Benchmark Table
  function renderAllRolesTable(rolesList) {
    const tbody = document.getElementById("allRolesTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    rolesList.forEach((r) => {
      let badgeClass = "bg-secondary";
      if (r.readiness_score >= 75) badgeClass = "bg-success";
      else if (r.readiness_score >= 55) badgeClass = "bg-primary";
      else if (r.readiness_score >= 40) badgeClass = "bg-warning";
      else badgeClass = "bg-danger";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="fw-bold">${r.role_title}</td>
        <td>
          <div class="d-flex align-items-center gap-2">
            <span class="fw-bold">${r.readiness_score}%</span>
            <div class="progress custom-progress flex-grow-1" style="height: 6px; max-width: 90px;">
              <div class="progress-bar ${badgeClass}" style="width: ${r.readiness_score}%;"></div>
            </div>
          </div>
        </td>
        <td><span class="badge ${badgeClass}-subtle text-${badgeClass.replace('bg-', '')}">${r.readiness_level}</span></td>
        <td>${r.matched_count} of ${r.total_required}</td>
        <td><span class="text-${r.missing_core_count > 0 ? "danger" : "success"} fw-bold">${r.missing_core_count}</span></td>
        <td><i class="bi bi-fire text-warning me-1"></i> ${r.market_demand}/10</td>
        <td>
          <button class="btn btn-sm btn-outline-primary btn-switch-role" data-role-id="${r.role_id}">
            View Gaps
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    document.querySelectorAll(".btn-switch-role").forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-role-id");
        if (roleSelector) {
          roleSelector.value = targetId;
          updateRoleSnapshot();
          form.dispatchEvent(new Event("submit"));
        }
      });
    });
  }

  // 14. Custom Job Description Analyzer
  const analyzeCustomJdBtn = document.getElementById("analyzeCustomJdBtn");
  const customJdInput = document.getElementById("customJdInput");
  const customJdResults = document.getElementById("customJdResults");

  if (analyzeCustomJdBtn && customJdInput && customJdResults) {
    analyzeCustomJdBtn.addEventListener("click", async () => {
      const jdText = customJdInput.value.trim();
      if (!jdText) {
        alert("Please paste the job description text first.");
        return;
      }

      const studentSkillsList = activeStudentSkills.size
        ? Array.from(activeStudentSkills)
        : (currentAnalysisData ? currentAnalysisData.candidate_profile.extracted_skills.map((s) => s.name) : []);

      analyzeCustomJdBtn.disabled = true;
      analyzeCustomJdBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span> Evaluating fit...`;

      try {
        const res = await fetch("/api/analyze-custom-jd", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ jd_text: jdText, student_skills: studentSkillsList }),
        });

        const data = await res.json();
        analyzeCustomJdBtn.disabled = false;
        analyzeCustomJdBtn.innerHTML = `<i class="bi bi-search"></i> Evaluate Fit Against This Job Description`;

        if (data.success) {
          const a = data.analysis;
          customJdResults.classList.remove("d-none");
          customJdResults.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0">Custom JD Match Score: <span class="gradient-text">${a.readiness_score}%</span></h5>
              <span class="badge bg-info-subtle text-info">NLP Semantic Match: ${a.nlp_similarity}%</span>
            </div>

            <div class="row g-3 mb-3">
              <div class="col-md-6">
                <div class="small fw-bold text-success mb-2">Matched Skills In Posting (${a.matched_skills.length}):</div>
                <div class="d-flex flex-wrap gap-1">
                  ${a.matched_skills.map((s) => `<span class="badge bg-success-subtle text-success p-2">${s}</span>`).join("") || '<span class="text-muted small">None</span>'}
                </div>
              </div>
              <div class="col-md-6">
                <div class="small fw-bold text-danger mb-2">Missing Skills from Posting (${a.missing_skills.length}):</div>
                <div class="d-flex flex-wrap gap-1">
                  ${a.missing_skills.map((s) => `<span class="badge bg-danger-subtle text-danger p-2">${s}</span>`).join("") || '<span class="text-muted small">None</span>'}
                </div>
              </div>
            </div>

            ${
              a.key_terms && a.key_terms.length
                ? `
              <div class="mt-3 pt-2 border-top border-secondary">
                <span class="small text-muted fw-semibold me-2">Top Key Terms in Job Posting:</span>
                ${a.key_terms.map((k) => `<span class="badge bg-secondary me-1">${k}</span>`).join("")}
              </div>
            `
                : ""
            }
          `;
          showToast("Custom Job Description fit analysis complete!");
        } else {
          alert(data.error || "Custom JD evaluation failed.");
        }
      } catch (err) {
        analyzeCustomJdBtn.disabled = false;
        analyzeCustomJdBtn.innerHTML = `<i class="bi bi-search"></i> Evaluate Fit Against This Job Description`;
        alert("Error: " + err.message);
      }
    });
  }

  // 15. ATS Power Verb Re-writer & Bullet Polisher Sandbox
  const btnPolishBullet = document.getElementById("btnPolishBullet");
  const rawBulletInput = document.getElementById("rawBulletInput");
  const bulletSkillInput = document.getElementById("bulletSkillInput");
  const bulletResultsContainer = document.getElementById("bulletResultsContainer");
  const bulletVariationsGrid = document.getElementById("bulletVariationsGrid");

  document.querySelectorAll(".ai-bullet-sample").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (rawBulletInput) rawBulletInput.value = btn.getAttribute("data-sample") || "";
      if (bulletSkillInput) bulletSkillInput.value = btn.getAttribute("data-skill") || "";
      showToast("Sample bullet loaded into polisher!");
    });
  });

  if (btnPolishBullet) {
    btnPolishBullet.addEventListener("click", async () => {
      const rawText = rawBulletInput ? rawBulletInput.value.trim() : "";
      if (!rawText) {
        alert("Please enter or select a bullet point to polish.");
        return;
      }

      const targetSkill = bulletSkillInput ? bulletSkillInput.value.trim() : "";
      btnPolishBullet.disabled = true;
      btnPolishBullet.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Polishing with Power Verbs...`;

      try {
        const res = await fetch("/api/ats/polish-bullet", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ bullet: rawText, skill: targetSkill }),
        });

        const data = await res.json();
        btnPolishBullet.disabled = false;
        btnPolishBullet.innerHTML = `<i class="bi bi-lightning-charge-fill"></i> Polish Bullet With Power Verbs`;

        if (data.success && data.result && data.result.variations) {
          bulletResultsContainer.classList.remove("d-none");
          bulletVariationsGrid.innerHTML = data.result.variations.map((v, idx) => `
            <div class="col-md-4">
              <div class="p-3 rounded-3 bg-dark-subtle border h-100 d-flex flex-column justify-content-between">
                <div>
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-${v.badge}-subtle text-${v.badge}">${v.type}</span>
                    <span class="badge bg-secondary" style="font-size: 0.7rem;">Action: ${v.power_verb}</span>
                  </div>
                  <p class="small text-light mb-2 font-monospace" id="var-text-${idx}" style="line-height: 1.5;">${v.text}</p>
                  <div class="small text-muted" style="font-size: 0.78rem;">
                    <i class="bi bi-graph-up text-success me-1"></i> Metric: ${v.metric_added}
                  </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-primary w-100 mt-3 btn-copy-var" data-target="var-text-${idx}">
                  <i class="bi bi-clipboard me-1"></i> Copy Bullet
                </button>
              </div>
            </div>
          `).join("");

          // Wire up copy buttons
          document.querySelectorAll(".btn-copy-var").forEach((cBtn) => {
            cBtn.addEventListener("click", () => {
              const targetId = cBtn.getAttribute("data-target");
              const textToCopy = document.getElementById(targetId).textContent.trim();
              navigator.clipboard.writeText(textToCopy);
              cBtn.innerHTML = `<i class="bi bi-check2 text-success me-1"></i> Copied!`;
              showToast("Polished bullet copied to clipboard!");
              setTimeout(() => {
                cBtn.innerHTML = `<i class="bi bi-clipboard me-1"></i> Copy Bullet`;
              }, 2000);
            });
          });

          showToast("Generated 3 recruiter-ready power bullet variations!");
        } else {
          alert(data.error || "Failed to polish bullet.");
        }
      } catch (err) {
        btnPolishBullet.disabled = false;
        btnPolishBullet.innerHTML = `<i class="bi bi-lightning-charge-fill"></i> Polish Bullet With Power Verbs`;
        alert("Error: " + err.message);
      }
    });
  }

  // Utility helpers
  function showLoading(show) {
    if (!loadingState) return;
    if (show) {
      loadingState.classList.remove("d-none");
      if (analyzeSubmitBtn) {
        analyzeSubmitBtn.disabled = true;
        analyzeSubmitBtn.querySelector("span").textContent = "Analyzing Skill Gap...";
      }
    } else {
      loadingState.classList.add("d-none");
      if (analyzeSubmitBtn) {
        analyzeSubmitBtn.disabled = false;
        analyzeSubmitBtn.querySelector("span").textContent = "Analyze Skill Gap & ATS Score";
      }
    }
  }

  function showError(msg) {
    if (errorMessage && errorAlert) {
      errorMessage.textContent = msg;
      errorAlert.classList.remove("d-none");
      errorAlert.scrollIntoView({ behavior: "smooth" });
    }
  }

  function hideError() {
    if (errorAlert) {
      errorAlert.classList.add("d-none");
    }
  }
});
