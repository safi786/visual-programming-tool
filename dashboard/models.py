from django.db import models
from django.conf import settings
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False, unique=True)
    description = models.TextField(max_length=500)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Library(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    version = models.FloatField(default=0.1, null=True, blank=True)
    code = models.TextField(null=False, blank=False)
    public_access = models.BooleanField(default=False)
    category_tag = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Library"
        verbose_name_plural = "Libraries"

    def get_absolute_url(self):
        return reverse('libraries')


class Provide(models.Model):
    class Meta:
        unique_together = (('library', 'category'),)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return "%s  %s" % (self.library, self.category)

class Depend(models.Model):
    class Meta:
        unique_together = (('library', 'category'),)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return "%s  %s" % (self.library, self.category)

class Project(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(max_length=500)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    public_access = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects')


class Program(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    orderNumber = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return "%s" % (self.project)


class ImportedProject(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.project)


class ImportedLibrary(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % (self.library)


class VarConfig(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    var_choices = (
        ('integer', 'integer'),
        ('string', 'string'),
        ('float', 'float')
    )
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    type = models.CharField(blank=False, null=False, max_length=7, choices=var_choices, default='string')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return "%s" % (self.name)

    class Meta:
        verbose_name = "Variable Config"
        verbose_name_plural = "Variable Configurations"


def generate_path(instance, filename):
    import os

    file_path = "Attachments/" + str(instance.library.id) + '/' + str(instance.user.id) + '/' + filename
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    return file_path


class FileConfig(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    variable_name = models.CharField(max_length=50, default="filename")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, )
    file = models.FileField(upload_to=generate_path, blank=False, null=False)
