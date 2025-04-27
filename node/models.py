from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import UserProfile

class Node(models.Model):
    """
    A task node that can nest infinitely. 
    Fields:
      - title, description, deadline, priority, status
      - parent → self-referential FK
      - children → reverse relation of parent
      - collaborators → many UserProfiles
    """

    class Status(models.TextChoices):
        ONGOING = 'ongoing', 'On Going'
        MISSED  = 'missed',  'Missed'
        DONE    = 'done',    'Done'

    class Priority(models.IntegerChoices):
        LOW    = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH   = 3, 'High'

    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    deadline     = models.DateTimeField(null=True, blank=True)
    priority     = models.PositiveSmallIntegerField(
                       choices=Priority.choices,
                       default=Priority.MEDIUM
                   )
    status       = models.CharField(
                       max_length=10,
                       choices=Status.choices,
                       default=Status.ONGOING
                   )
    parent       = models.ForeignKey(
                       'self',
                       null=True,
                       blank=True,
                       related_name='children',
                       on_delete=models.CASCADE
                   )
    collaborators = models.ManyToManyField(
                       UserProfile,
                       related_name='nodes',
                       blank=True
                   )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Prevent circular nesting: a node cannot be its own ancestor.
        """
        ancestor = self.parent
        while ancestor:
            if ancestor == self:
                raise ValidationError("Cannot set a node as its own ancestor.")
            ancestor = ancestor.parent

    def save(self, *args, **kwargs):
        # Always validate before saving
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
