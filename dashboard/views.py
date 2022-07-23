from django.contrib.auth.models import User
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ProjectForm, LibraryForm, ProgramForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.db import transaction
from .models import *
from .forms import *
from django.db.models import Q
import json


#######################################################################################################################
#                                             Project Views                                                           #
#######################################################################################################################


class ProjectCreate(CreateView):
    model = Project
    template_name = "Project/project_create_form.html"
    form_class = ProjectForm
    success_url = None

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()
        return super(ProjectCreate, self).form_valid(form)

    def form_invalid(self, form):
        errors = form.errors
        return HttpResponse(json.dumps(errors), status=400)

    def get_success_url(self):
        return reverse_lazy('project-update', kwargs={'pk': self.object.pk})


class ProjectUpdate(UpdateView):
    model = Project
    template_name = "Project/project_update_form.html"
    form_class = ProjectForm

    def get_context_data(self, **kwargs):
        data = super(ProjectUpdate, self).get_context_data(**kwargs)
        data['programs'] = ProgramForm(instance=self.object)
        return data

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.author = self.request.user

            self.object = form.save()
        return super(ProjectUpdate, self).form_valid(form)

    def form_invalid(self, form):
        errors = form.errors
        return HttpResponse(json.dumps(errors), status=400)


    def get_success_url(self):
        return reverse_lazy('project', kwargs={'pk': self.object.pk})


def addLibrary(request, pk):
    if request.method == "POST":
        try:
            instance = Project.objects.get(id=pk)
        except Project.DoesNotExist:
            instance = None
        criterion2 = Q(project=instance)
        programs = Program.objects.filter(criterion2)
        if 'form1' in request.POST:
            program = ProgramForm(request.POST, initial={'programs': programs})
            # program = ProgramForm(request.POST)
            if program.is_valid():
                obj = program.save(commit=False)
                obj.project = instance
                obj.save()
            # project = ProjectForm(instance=instance)
            # # program = ProgramForm(instance=instance, initial={'programs': programs})
            # criterion2 = Q(project=instance)
            # programs = Program.objects.filter(criterion2)
            # program.initial = None
            # # program = ProgramForm()
                project = ProjectForm(instance=instance)

                criterion2 = Q(project=instance)
                programs = Program.objects.filter(criterion2)
                if programs:
                    highest_order = max(programs.all().values_list('orderNumber'))[0] + 1
                else:
                    highest_order = 1
                program = ProgramForm(instance=instance, initial={'programs': programs, 'orderNumber':highest_order})
                return render(request, 'Project/project_update_form.html', context = {'project': project, 'program': program, 'programs': programs})
            else:
                errors = program.errors
                return HttpResponse(json.dumps(errors), status=400)
        elif 'form' in request.POST:
            project = ProjectForm(request.POST, instance=instance)
            if project.is_valid():
                project.save()
                if programs:
                    highest_order = max(programs.all().values_list('orderNumber'))[0] + 1
                else:
                    highest_order = 1
                program = ProgramForm(initial={'orderNumber':highest_order})
                criterion2 = Q(project=instance)
                programs = Program.objects.filter(criterion2)
                return render(request, 'Project/project_update_form.html', context = {'project': project, 'program': program, 'programs': programs})
            else:
                errors = project.errors
                return HttpResponse(json.dumps(errors), status=400)
    else:
        try:
            instance = Project.objects.get(id=pk)
        except Project.DoesNotExist:
            instance = None
        project = ProjectForm(instance=instance)

        criterion2 = Q(project=instance)
        programs = Program.objects.filter(criterion2)
        if programs:
            highest_order = max(programs.all().values_list('orderNumber'))[0] + 1
        else:
            highest_order = 1
        program = ProgramForm(instance=instance, initial={'programs': programs, 'orderNumber':highest_order})
    return render(request, 'Project/project_update_form.html', context = {'project': project, 'program': program, 'programs': programs})


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 10
    template_name = "Project/project_list.html"
    context_object_name = 'projects'

    def get_queryset(self):
        criterion2 = Q(author=self.request.user)
        q = Project.objects.filter(criterion2)
        return q


class PublicProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 10
    template_name = "Project/public_project_list.html"
    context_object_name = 'projects'

    def get_queryset(self):
        criterion2 = Q(public_access=True)
        q = Project.objects.filter(criterion2)
        return q


class ImportedProjectListView(LoginRequiredMixin, ListView):
    model = Project
    paginate_by = 10
    template_name = "Project/imported_project_list.html"
    context_object_name = 'projects'

    def get_queryset(self):
        criterion2 = Q(user=self.request.user)
        q = ImportedProject.objects.filter(criterion2)
        return q


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "Project/project_create_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            data['programs'] = ProgramForm(self.request.POST, instance=self.object)
        else:
            context['programs'] = ProgramForm(self.request.POST)

        return context


class ProjectDeleteView(DeleteView):
    model = Project
    form_class = ProjectForm
    template_name = "Project/confirm_delete.html"
    success_url = reverse_lazy('projects')

class ImportedProjectDeleteView(DeleteView):
    model = ImportedProject
    form_class = ImportedProjectForm
    template_name = "Project/confirm_delete.html"
    success_url = reverse_lazy('imported-projects')


def projectUpdate(request, id):
    id = int(id)
    try:
        project_sel = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return redirect('index')
    project_form = ProjectForm(request.POST or None, instance=project_sel)
    if project_form.is_valid():
        project_form.save()

    program_sel = Program.objects.filter(project__id=id)
    return render(request, 'dashboard/project-view.html', {'project': project_form, 'program': program_sel})


def ImportProject(request, id):
    id = int(id)
    try:
        project_sel = Project.objects.get(id=id)
        # project_form = ImportedProjectForm(request.POST or None, instance=project_sel)
        user = request.user

        gta = ImportedProject.objects.create(project=project_sel, user=user)
        programs = Program.objects.filter(project__id=id)
        for program in programs:
            lib = program.library
            varConfigs = VarConfig.objects.filter(library__id=lib.id, user__id=lib.author.id)
            for obj in varConfigs:
                obj.pk = None
                obj.user = request.user
                obj.save()
            fileConfigs = FileConfig.objects.filter(library__id=lib.id, user__id=lib.author.id)
            for obj in fileConfigs:
                obj.pk = None
                obj.user = request.user
                obj.save()

        return render(request, 'Project/public_project_list.html',
                      {'success': "Project has been successfully imported."})

    except Project.DoesNotExist:
        return redirect('index')


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)

                return redirect('login')

        context = {'form': form}
        return render(request, 'dashboard/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')

        context = {}
        return render(request, 'dashboard/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    libraries_count = Library.objects.all().count()
    my_libraries_count = Library.objects.filter(author=request.user).count()
    projects_count = Project.objects.all().count()
    my_projects_count = Project.objects.filter(author=request.user).count()
    return render(request, 'dashboard/dashboard.html', context={"libraries_count": libraries_count, "my_libraries_count": my_libraries_count, "projects_count": projects_count, "my_projects_count": my_projects_count})
    # return render(request, 'dashboard/index.html', context={"form": 3})



@login_required(login_url='login')
def project(request, pk):
    my_project = Project.objects.get(id=pk)
    programs = Program.objects.filter(project__id=pk)
    return render(request, 'dashboard/project-view.html', {'project': my_project, 'program': programs})


from extra_views import CreateWithInlinesView, UpdateWithInlinesView, InlineFormSetFactory


class ProgramInline(InlineFormSetFactory):
    model = Program
    fields = ['project', 'library', 'orderNumber']


# class ProjectCreate(LoginRequiredMixin, CreateWithInlinesView):
#     model = Project
#     fields = ['name', 'description']
#     inlines = [ProgramInline]
#     template_name = "Project/project_create_form.html"
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)

# class ProjectCreate(LoginRequiredMixin, CreateView):
#     form_class = ProjectForm
#     template_name = "Project/project_create_form.html"
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)

# def get_context_data(self, **kwargs):
#     context = super().get_context_data(**kwargs)
#     context['programs'] = Program.objects.filter(project__id=self.object.id)
#     return context

##########################################################################
#                           Library views                             #
##########################################################################


class LibraryListView(LoginRequiredMixin, ListView):
    model = Library
    paginate_by = 10
    template_name = "Library/library_list.html"
    context_object_name = 'libraries'

    def get_queryset(self):
        criterion2 = Q(author=self.request.user)
        q = Library.objects.filter(criterion2)
        return q


class PublicLibraryListView(LoginRequiredMixin, ListView):
    model = Library
    paginate_by = 10
    template_name = "Library/public_library_list.html"
    context_object_name = 'libraries'

    def get_queryset(self):
        criterion2 = Q(public_access=True)
        q = Library.objects.filter(criterion2)
        return q


class ImportedLibraryListView(LoginRequiredMixin, ListView):
    model = Library
    paginate_by = 10
    template_name = "Library/imported_library_list.html"
    context_object_name = 'libraries'

    def get_queryset(self):
        criterion2 = Q(user=self.request.user)
        q = ImportedLibrary.objects.filter(criterion2)
        return q


class LibraryCreate(LoginRequiredMixin, CreateView):
    model = Library
    template_name = "Library/library_formset_create_form.html"
    # template_name = "Library/library_formset_create_form.html"
    form_class = LibraryForm
    success_url = None

    # def form_valid(self, form):
    #     form.instance.author = self.request.user
    #     return super().form_valid(form)
    def get_context_data(self, **kwargs):
        data = super(LibraryCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['VarConfigs'] = VarCongigFormSet(self.request.POST)
            data['FileConfigs'] = FileCongigFormSet(self.request.POST, self.request.FILES)
            data['Provides'] = ProvideFormSet(self.request.POST)
            data['Depends'] = DependFormSet(self.request.POST)
        else:
            data['VarConfigs'] = VarCongigFormSet()
            data['FileConfigs'] = FileCongigFormSet()
            data['Provides'] = ProvideFormSet()
            data['Depends'] = DependFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        VarConfigs = context['VarConfigs']
        FileConfigs = context['FileConfigs']
        Provides = context['Provides']
        Depends = context['Depends']
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()
            if VarConfigs.is_valid():
                try:
                    VarConfigs.instance = self.object
                    VarConfigs.instance.user = self.request.user
                    VarConfigs.save()
                except:
                    print(VarConfigs._errors)
            if FileConfigs.is_valid():
                try:
                    FileConfigs.instance = self.object
                    FileConfigs.instance.user = self.request.user
                    FileConfigs.save()
                except:
                    print("Error occured in File Config saving!")
            if Provides.is_valid():
                try:
                    Provides.instance = self.object
                    Provides.save()
                except:
                    print("Error occured in Provide saving!")
            if Depends.is_valid():
                try:
                    Depends.instance = self.object
                    Depends.save()
                except:
                    print("Error occured in Depend saving!")

        return super(LibraryCreate, self).form_valid(form)


    # def form_invalid(self, form):
    #     print("invalid form", form)
    def get_success_url(self):
        return reverse_lazy('library', kwargs={'pk': self.object.pk})


class LibraryUpdateView(LoginRequiredMixin, UpdateView):
    model = Library
    # template_name = "Library/library_create_form.html"
    template_name = "Library/library_formset_create_form.html"
    form_class = LibraryForm

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['programs'] = Program.objects.filter(project__id=self.object.id)
    #     return context
    def get_context_data(self, **kwargs):
        data = super(LibraryUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['VarConfigs'] = VarCongigFormSet(self.request.POST, instance=self.object)
            data['FileConfigs'] = FileCongigFormSet(self.request.POST, self.request.FILES, instance=self.object)
            data['Provides'] = ProvideFormSet(self.request.POST, instance=self.object)
            data['Depends'] = DependFormSet(self.request.POST, instance=self.object)
        else:
            data['VarConfigs'] = VarCongigFormSet(instance=self.object)
            data['FileConfigs'] = FileCongigFormSet(instance=self.object)
            data['Provides'] = ProvideFormSet(instance=self.object)
            data['Depends'] = DependFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        VarConfigs = context['VarConfigs']
        FileConfigs = context['FileConfigs']
        Provides = context['Provides']
        Depends = context['Depends']
        with transaction.atomic():
            form.instance.author = self.request.user
            self.object = form.save()
            if VarConfigs.is_valid():
                try:
                    VarConfigs.instance = self.object
                    VarConfigs.instance.user = self.request.user
                    VarConfigs.save()
                except:
                    print(VarConfigs._errors)
            if FileConfigs.is_valid():
                try:
                    FileConfigs.instance = self.object
                    FileConfigs.instance.user = self.request.user
                    FileConfigs.save()
                except Exception as e:
                    print(e)
            if Provides.is_valid():
                try:
                    Provides.instance = self.object
                    Provides.save()
                except:
                    print("Error occured in Provide saving!")
            if Depends.is_valid():
                try:
                    Depends.instance = self.object
                    Depends.save()
                except:
                    print("Error occured in Depend saving!")

        return super(LibraryUpdateView, self).form_valid(form)

class LibraryDeleteView(DeleteView):
    model = Library
    form_class = LibraryForm
    success_url = '/libraries'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

class ProgramDeleteView(DeleteView):
    model = Program
    form_class = ProgramForm

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('project-update', kwargs={'pk': self.object.project.id})


@login_required(login_url='login')
def libraryView(request, pk):
    library = Library.objects.get(id=pk)
    config_var = VarConfig.objects.filter(library_id=pk)

    # print("library", library.code)
    return render(request, 'dashboard/library-view.html', context={"library": library, "config_vars": config_var})


@login_required(login_url='login')
def libraryEdit(request, pk):
    library = Library.objects.get(id=pk)
    print("library", library.code)
    return render(request, 'dashboard/library-edit.html', {'library': library})


@login_required(login_url='login')
def index(request):
    libraries_count = Library.objects.all().count()
    my_libraries_count = Library.objects.filter(author=request.user).count()
    # return render(request, 'dashboard/index.html', context={"libraries_count": 2, "my_libraries_count": 5})
    return render(request, 'dashboard/index.html', context={"form": 3})


def add_data(auth_id, lib_id, conf_vars):
    return """
import pickle
import os
a = 7
b = 3
c = 5
filename = 'Pickles/""" + str(auth_id) + """/""" + str(lib_id) + """/""" + """filename.pickle'
os.makedirs(os.path.dirname(filename), exist_ok=True)
with open(filename, 'wb') as handle:
    pickle.dump([a, b, c], handle, protocol=pickle.HIGHEST_PROTOCOL)
    """


def get_data(auth_id, lib_id, conf_vars):
    return """
import pickle
print("config variables are ", conf_vars)
filename = 'Pickles/""" + str(auth_id) + """/""" + str(lib_id) + """/""" + """filename.pickle'
with open(filename, 'rb') as file:
    conf_vars = pickle.load(file)
"""


@login_required(login_url='login')
def run_code(request, pk):
    programs = Program.objects.filter(project__id=pk).order_by('orderNumber')

    f = StringIO()
    # sys.stderr = sys.stdout
    s = None
    with redirect_stdout(f):
        exec("print('Project : ', programs[0].project.name)")
        exec("print('')")
        exec("print('')")
        for program in programs:
            try:
                criterion1 = Q(user__id=request.user.id)
                criterion2 = Q(library__id=program.library.id)
                conf_vars = VarConfig.objects.filter(criterion1 & criterion2)
                for ins in conf_vars:
                    if ins.type == 'integer':
                        locals()[ins.name] = int(ins.value)
                    elif ins.type == 'float':
                        locals()[ins.name] = float(ins.value)
                    else:
                        locals()[ins.name] = ins.value
                criterion1 = Q(user__id=request.user.id)
                criterion2 = Q(library__id=program.library.id)
                conf_files = FileConfig.objects.filter(criterion1 & criterion2)
                for ins in conf_files:
                    locals()[ins.variable_name] = ins.file.path

                # exec(get_data(request.user.id, program.library.id, arr))
                exec("print('Running Library : ', program.library.name)")
                exec("print('')")
                exec(program.library.code)
                exec("print('')")
                exec("print('')")
                # exec(str(print(x)))
            # except NameError as err:
            #     print(err)
            except Exception as e:
                print(e)

            s = f.getvalue()
    if s:
        s = s.replace('\n', '<br />')
        html = "<html><body><p>%s</p></body></html>" % s
    else:
        html = "<html><body><p>This project has no output</p></body></html>"
    return HttpResponse(html)
