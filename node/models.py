from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import UserProfile
from django.dispatch import receiver
from django.db.models.signals import m2m_changed, post_save
from django.utils import timezone

class NodeManager(models.Manager):
    def get_root_nodes(self, user):
        """
        Return all top-level nodes (parent=None) where `user` is a collaborator.
        """
        profile = UserProfile.objects.get(username=user.username)
        return self.filter(parent__isnull=True, collaborators=profile)
    
    def update_missed_nodes(self):
        """
        Mark any ONGOING nodes whose deadline < now() as MISSED.
        Returns count of updated records.
        """
        now = timezone.now()
        qs = self.filter(status=Node.Status.ONGOING, deadline__lt=now)
        # .update() returns number of rows affected
        return qs.update(status=Node.Status.MISSED)

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
    completed_subtasks = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    # Add a flag to prevent recursive saves
    _is_updating_subtask_count = False

    objects = NodeManager()

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
        
        # Check if node has a parent and we're not in an update cycle
        has_parent = self.parent is not None
        
        # Detect if this is an existing record (has pk) being updated
        is_update = self.pk is not None
        
        # First save the node
        super().save(*args, **kwargs)
        
        # Update parent after saving for any status change (both to DONE or from DONE)
        # but only if we're not already in an update cycle
        if has_parent and is_update and not self._is_updating_subtask_count:
            self.update_parent_completed_subtasks()
    
    def update_parent_completed_subtasks(self):
        """
        Updates the parent's completed_subtasks count and status if needed.
        """
        if self.parent:
            # Count completed children for the parent
            completed_count = self.parent.children.filter(status=self.Status.DONE).count()
            total_count = self.parent.children.count()
            
            # Update the parent's completed_subtasks
            self.parent._is_updating_subtask_count = True
            try:
                self.parent.completed_subtasks = completed_count
                
                # Check if parent status should be updated
                if completed_count == total_count and total_count > 0:
                    # All children are done, mark parent as done
                    self.parent.status = self.Status.DONE
                elif completed_count < total_count and self.parent.status == self.Status.DONE:
                    # Not all children are done but parent is marked as done,
                    # revert parent back to ONGOING
                    self.parent.status = self.Status.ONGOING
                
                # Use update() to avoid triggering signals
                Node.objects.filter(pk=self.parent.pk).update(
                    completed_subtasks=completed_count,
                    status=self.parent.status
                )
                
                # Refresh from database since we bypassed signals
                self.parent.refresh_from_db()
                
                # Continue up the tree - propagate changes upward regardless of status
                if self.parent.parent:
                    self.parent.update_parent_completed_subtasks()
            finally:
                self.parent._is_updating_subtask_count = False

    def get_all_child_nodes(self, filter_by_user=False, user=None, max_depth=None):
        """
        Recursively collect descendants up to max_depth.
        max_depth=1 → immediate children only
        max_depth=None → infinite nesting
        """
        if filter_by_user and user is None:
            raise ValueError("Must provide `user` when filter_by_user=True")

        collected = []

        def _recurse(node, depth):
            if max_depth is not None and depth > max_depth:
                return
            for child in node.children.all():
                if not filter_by_user or (user.userprofile in child.collaborators.all()):
                    collected.append(child)
                    _recurse(child, depth + 1)

        _recurse(self, 1)
        return collected

    def __str__(self):
        return self.title

# ——— PROPAGATE collaborator "up" the tree ———

@receiver(m2m_changed, sender=Node.collaborators.through)
def _propagate_collaborator(sender, instance, action, pk_set, **kwargs):
    """
    Whenever someone is added to instance.collaborators,
    bubble them up to all ancestor nodes.
    """
    if action == 'post_add':
        # pk_set is a set of UserProfile PKs just added to instance.collaborators
        for userprofile_pk in pk_set:
            parent = instance.parent
            while parent:
                # .add(...) is idempotent
                parent.collaborators.add(userprofile_pk)
                parent = parent.parent

