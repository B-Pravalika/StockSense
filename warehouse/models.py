from django.db import models


class Warehouse(models.Model):
    name = models.CharField(max_length=150, unique=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='locations'
    )

    name = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['warehouse', 'name'],
                name='unique_location_per_warehouse'
            )
        ]

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"