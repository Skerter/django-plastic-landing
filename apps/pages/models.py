from django.db import models


class Certificate(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="certificates/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"

    def __str__(self):
        return self.title
