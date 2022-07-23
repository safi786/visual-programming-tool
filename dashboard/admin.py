from django.contrib import admin
from .models import *


# Register your models here.
class ProgramInLine(admin.TabularInline):
    model = Program
    extra = 1


class VarConfigInLine(admin.TabularInline):
    model = VarConfig
    extra = 1


class FileConfigInLine(admin.TabularInline):
    model = FileConfig
    extra = 1

class ProvideInLine(admin.TabularInline):
    model = Provide
    extra = 1


class DependInLine(admin.TabularInline):
    model = Depend
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProgramInLine]
    list_display = [field.name for field in Project._meta.fields if field.name != "id"]
    list_filter = [field.name for field in Project._meta.fields if field.name != "id"]

class LibraryAdmin(admin.ModelAdmin):
    inlines = [VarConfigInLine, FileConfigInLine, ProvideInLine, DependInLine]
    list_display = [field.name for field in Library._meta.fields if field.name != "id"]
    list_filter = [field.name for field in Library._meta.fields if field.name != "id"]

class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields if field.name != "id"]
    list_filter = ("name",)

class ImportedProjectAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ImportedProject._meta.fields if field.name != "id"]
    list_filter = [field.name for field in ImportedProject._meta.fields if field.name != "id"]


class ImportedLibraryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ImportedLibrary._meta.fields if field.name != "id"]
    list_filter = [field.name for field in ImportedLibrary._meta.fields if field.name != "id"]


admin.site.register(Library, LibraryAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ImportedProject, ImportedProjectAdmin)
admin.site.register(ImportedLibrary, ImportedLibraryAdmin)