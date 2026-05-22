from django.db import models


class ComplaintAnalysis(models.Model):
    complaint_text = models.TextField()
    category = models.CharField(max_length=100)
    urgency = models.CharField(max_length=50)
    priority = models.CharField(max_length=100)
    eligibility = models.CharField(max_length=200)
    resolution_steps = models.TextField()
    estimated_time = models.CharField(max_length=100)
    success_probability = models.CharField(max_length=50)
    confidence_score = models.FloatField()
    preventive_advice = models.TextField()
    timeline = models.TextField()
    mermaid_code = models.TextField()
    official_links = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category