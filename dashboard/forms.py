from django.contrib.auth.forms import UserCreationForm
from django.forms.models import inlineformset_factory
from django.contrib.auth.models import User
from .models import *
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML, ButtonHolder, Submit, Row
from .custom_layout_object import *
from django.forms import Textarea
from django.db.models import Q

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ['author']
        # working perfectly
        # widgets = {
        #     'name': Textarea(attrs={'cols': 80, 'rows': 5}),
        # }
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        # self.fields['username'].required = False
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            # visible.field.label.attrs['class'] = 'short-heading mb-2'
            visible.field.widget.attrs['placeholder'] = visible.field.label

    # def __init__(self, *args, **kwargs):
    #     super(ProjectForm, self).__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.form_tag = False
    #     # self.helper.form_class = 'form-horizontal'
    #     # self.helper.label_class = 'col-md-3 create-label'
    #     # self.helper.field_class = 'col-md-9'
    #     self.helper.layout = Layout(
    #         Div(
    #
    #             Field('name', css_class='hello'),
    #             Field('description'),
    #             Fieldset('Add Libraries',
    #                      Formset('programs')),
    #
    #         )
    #     )


class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = '__all__'
        exclude = ['author']

    def __init__(self, *args, **kwargs):
        super(LibraryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        # self.helper.form_class = 'form-horizontal'
        # self.helper.label_class = 'col-md-3 create-label'
        # self.helper.field_class = 'col-md-9'
        self.helper.layout = Layout(
            Div(

                Row(
                    Div('name', css_class='col-md-4'),
                    Div('category_tag', css_class='col-md-4'),
                    Div('public_access', css_class='col-md-4'),

                ),

                Field('code'),


                HTML("""</div>
                                <!-- /.card-body -->
                            </div>
                            <!-- /.card -->
                        </div>
                    </div>"""),
                HTML("""<div class="col-md-12">
                            <div class="card card-info">
                                <div class="card-header" style="background-color: #58789b;">
                                    <h3 class="card-title">Variable Configuration</h3>
            
                                    <div class="card-tools">
                                        <button type="button" class="btn btn-tool" data-card-widget="collapse" title="Collapse">
                                            <i class="fas fa-minus"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="card-body">
                                """),
                Fieldset('',
                         VarConfigFormset('VarConfigs')),
                HTML("""
                                </div>
                                <!-- /.card-body -->
                            </div>
                            <!-- /.card -->
                        </div>"""),
                HTML("""<div class="col-md-12">
                    <div class="card card-info">
                        <div class="card-header" style="background-color: #58789b;">
                            <h3 class="card-title">File Configurations</h3>

                            <div class="card-tools">
                                <button type="button" class="btn btn-tool" data-card-widget="collapse" title="Collapse">
                                    <i class="fas fa-minus"></i>
                                </button>
                            </div>
                        </div>
                        <div class="card-body">
                        """),
                Fieldset('', VarConfigFormset('FileConfigs')),
                HTML("""
                        </div>
                        <!-- /.card-body -->
                    </div>
                    <!-- /.card -->
                </div>"""),

                HTML("""<div class="col-md-6">
                            <div class="card card-success">
                                <div class="card-header" style="background-color: #58789b;">
                                    <h3 class="card-title">Depends</h3>

                                    <div class="card-tools">
                                        <button type="button" class="btn btn-tool" data-card-widget="collapse" title="Collapse">
                                            <i class="fas fa-minus"></i>
                                        </button>
                                    </div>
                                </div>
                                <div class="card-body">
                                """),
                Fieldset('', DependFormset('Depends')),
                HTML("""
                                </div>
                                <!-- /.card-body -->
                            </div>
                            <!-- /.card -->
                        </div>"""),
                HTML("""<div class="col-md-6">
                                    <div class="card card-danger">
                                        <div class="card-header" style="background-color: #58789b;">
                                            <h3 class="card-title">Provides</h3>

                                            <div class="card-tools">
                                                <button type="button" class="btn btn-tool" data-card-widget="collapse" title="Collapse">
                                                    <i class="fas fa-minus"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <div class="card-body">
                                        """),
                Fieldset('', ProvideFormset('Provides')),
                HTML("""
                                        </div>
                                        <!-- /.card-body -->
                                    </div>
                                    <!-- /.card -->
                                </div>"""),
                HTML("<br>"),
            )
        )


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProgramForm, self).__init__(*args, **kwargs)
        initial = kwargs.get('initial', None)
        programs = initial.get('programs', None)

        dependent_categories = Depend.objects.all().values_list('library__category_tag_id', flat=True)
        independent_categories = Category.objects.exclude(id__in=dependent_categories).values_list('id', flat=True)
        categories = list(set(independent_categories))
        categories_of_existing_libraries = list(set(programs.all().values_list('library__category_tag__id', flat=True)))
        categories.extend(categories_of_existing_libraries)
        categories_of_depending_libraries = Depend.objects.filter(category_id__in=categories_of_existing_libraries).values_list('library__category_tag__id', flat=True)
        categories.extend(categories_of_depending_libraries)
        categories_of_providing_libraries = Provide.objects.filter(
            category_id__in=categories_of_existing_libraries).values_list('library__category_tag__id', flat=True)
        categories.extend(categories_of_providing_libraries)
        categories = list(set(categories))

        self.fields['library'].queryset = Library.objects.filter(category_tag__id__in=categories)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            # visible.field.label.attrs['class'] = 'short-heading mb-2'
            visible.field.widget.attrs['placeholder'] = visible.field.label


class ImportedProjectForm(forms.ModelForm):
    class Meta:
        model = ImportedProject
        fields = '__all__'


class VarConfigForm(forms.ModelForm):
    class Meta:
        model = VarConfig
        fields = '__all__'
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput()}

class FileConfigForm(forms.ModelForm):
    class Meta:
        model = FileConfig
        fields = '__all__'
        # exclude = ['user']
        widgets = {'user': forms.HiddenInput()}


class ProvideForm(forms.ModelForm):
    class Meta:
        model = Provide
        fields = '__all__'


class DependForm(forms.ModelForm):
    class Meta:
        model = Depend
        fields = '__all__'


# ProgramFormSet = inlineformset_factory(
#     Project, Program, form=ProgramForm, extra=1, can_delete=True
# )

VarCongigFormSet = inlineformset_factory(
    Library, VarConfig, form=VarConfigForm, extra=1, can_delete=True
)

FileCongigFormSet = inlineformset_factory(
    Library, FileConfig, form=FileConfigForm, extra=1, can_delete=True
)

ProvideFormSet = inlineformset_factory(
    Library, Provide, form=ProvideForm, extra=1, can_delete=True
)

DependFormSet = inlineformset_factory(
    Library, Depend, form=DependForm, extra=1, can_delete=True
)
