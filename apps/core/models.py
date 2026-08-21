from django.db import models


class ContactInquiry(models.Model):
    name = models.CharField(max_length=120, verbose_name="Client Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=30, blank=True, verbose_name="Phone / WhatsApp")
    subject = models.CharField(max_length=200, verbose_name="Project / Subject")
    message = models.TextField(verbose_name="Inquiry Message")
    is_read = models.BooleanField(default=False, verbose_name="Read Status")
    is_replied = models.BooleanField(default=False, verbose_name="Replied")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date Received")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Client Inquiry"
        verbose_name_plural = "Client Inquiries"

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%b %d, %Y')})"
