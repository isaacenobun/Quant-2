from django.db import models

# Create your models here.

class block_model(models.Model):
    width = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    height = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    length = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    layer = models.CharField(max_length=100, blank=False)
    # mortar = models.IntegerField(blank=False)

    def __str__(self):
        return f'W-{self.width} H-{self.height} L-{self.length} Layer-{self.layer}'
    
class door_model(models.Model):
    width = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    height = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    quantity = models.IntegerField(blank=False)

    def __str__(self):
        return f'W-{self.width} H-{self.height} Q-{self.quantity}'
    
class window_model(models.Model):
    width = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    height = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    quantity = models.IntegerField(blank=False)

    def __str__(self):
        return f'W-{self.width} H-{self.height} Q-{self.quantity}'
    
class opening_model(models.Model):
    area = models.DecimalField(blank=False, decimal_places=2, max_digits=5)
    quantity = models.IntegerField(blank=False)

    def __str__(self):
        return f'A-{self.area} Q-{self.quantity}'