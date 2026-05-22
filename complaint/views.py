from django.shortcuts import render, get_object_or_404
from django.http import FileResponse

from .forms import ComplaintForm
from .models import ComplaintAnalysis
from .analyzer import analyze_complaint
from .pdf_utils import generate_pdf


def json_to_text(value):
    """
    Convert lists/dicts to readable text for database storage.
    """
    if isinstance(value, list):
        return "\n".join(str(v) for v in value)

    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            lines.append(f"{k}: {v}")
        return "\n".join(lines)

    return str(value)


def normalize_result(result):
    """
    Ensure all fields expected by result.html exist and are in proper format.
    """

    # ---------- Lists ----------
    list_fields = [
        "resolution_steps",
        "timeline",
        "preventive_advice",
        "similar_cases",
    ]

    for field in list_fields:
        value = result.get(field, [])

        if isinstance(value, str):
            value = [value] if value.strip() else []

        elif isinstance(value, dict):
            value = [f"{k}: {v}" for k, v in value.items()]

        elif value is None:
            value = []

        result[field] = value

    # ---------- Top Predictions ----------
    top_predictions = result.get("top_predictions", [])

    cleaned_predictions = []

    for pred in top_predictions:
        if isinstance(pred, dict):
            label = (
                pred.get("label")
                or pred.get("category")
                or pred.get("class")
                or ""
            )

            probability = (
                pred.get("probability")
                or pred.get("score")
                or pred.get("confidence")
                or 0
            )

            if label:
                cleaned_predictions.append({
                    "label": label.replace("_", " ").title(),
                    "probability": float(probability),
                })

        elif isinstance(pred, (list, tuple)) and len(pred) >= 2:
            cleaned_predictions.append({
                "label": str(pred[0]).replace("_", " ").title(),
                "probability": float(pred[1]),
            })

    result["top_predictions"] = cleaned_predictions

    # ---------- Confidence ----------
    confidence = (
        result.get("confidence")
        or result.get("confidence_score")
        or 0
    )

    try:
        confidence = float(confidence)

        # Convert 0.9998 → 99.98
        if confidence <= 1:
            confidence *= 100

    except Exception:
        confidence = 0

    result["confidence_score"] = round(confidence, 2)

    # ---------- Success Probability ----------
    success = result.get("success_probability", 0)

    try:
        success = float(success)
        if success <= 1:
            success *= 100
    except Exception:
        success = 0

    result["success_probability"] = round(success, 2)

    # ---------- Flowchart ----------
    if "flowchart" not in result and "mermaid_code" in result:
        result["flowchart"] = result["mermaid_code"]

    # ---------- Official Resources ----------
    if "official_resources" not in result:
        result["official_resources"] = {
            "rbi_cms": "https://cms.rbi.org.in",
            "helpline": "14448",
            "email": "crpc@rbi.org.in",
        }

    # ---------- Defaults ----------
    defaults = {
        "category": "Unknown",
        "urgency": "Medium",
        "priority": "Normal",
        "eligibility": "Eligible After Bank Complaint",
        "estimated_time": "3-7 working days",
        "rag_context": "No additional context available.",
        "flowchart": "",
    }

    for key, value in defaults.items():
        if key not in result or result[key] in [None, ""]:
            result[key] = value

    return result


def home(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)

        if form.is_valid():
            complaint_text = form.cleaned_data["complaint_text"]

            # Analyze complaint
            result = analyze_complaint(complaint_text)

            # Normalize data for template
            result = normalize_result(result)

            # Save to database
            analysis = ComplaintAnalysis.objects.create(
                complaint_text=complaint_text,
                category=result.get("category", ""),
                urgency=result.get("urgency", ""),
                priority=result.get("priority", ""),
                eligibility=result.get("eligibility", ""),
                resolution_steps=json_to_text(
                    result.get("resolution_steps", [])
                ),
                estimated_time=result.get("estimated_time", ""),
                success_probability=str(
                    result.get("success_probability", "")
                ),
                confidence_score=float(
                    result.get("confidence_score", 0)
                ),
                preventive_advice=json_to_text(
                    result.get("preventive_advice", [])
                ),
                timeline=json_to_text(
                    result.get("timeline", [])
                ),
                mermaid_code=result.get("flowchart", ""),
                official_links=json_to_text(
                    result.get("official_resources", {})
                ),
            )

            return render(
                request,
                "complaint/result.html",
                {
                    "result": result,
                    "analysis": analysis,
                },
            )

    else:
        form = ComplaintForm()

    return render(
        request,
        "complaint/home.html",
        {
            "form": form,
        },
    )


def download_pdf(request, analysis_id):
    analysis = get_object_or_404(
        ComplaintAnalysis,
        id=analysis_id
    )

    pdf = generate_pdf(analysis)

    return FileResponse(
        pdf,
        as_attachment=True,
        filename="complaint_report.pdf"
    )