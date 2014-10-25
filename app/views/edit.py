from django.views.generic import FormView
from django.views.generic.edit import FormMixin, ProcessFormView, TemplateResponseMixin
from django.shortcuts import HttpResponseRedirect, render_to_response


class FormsetMixin(FormMixin):
    formset_class = None

    def get_formset_class(self):
        return self.formset_class

    def get_formset(self, formset_class):
        return formset_class(**self.get_form_kwargs())

    def form_valid(self, request, form, formset):
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, request, form, formset):
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class ProcessFormsetView(ProcessFormView):
    def get(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)

        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(request, form, formset)
        else:
            return self.form_invalid(request, form, formset)


class BaseFormsetView(FormsetMixin, ProcessFormsetView):
    """
    A base view for displaying a form
    """


class FormsetView(TemplateResponseMixin, BaseFormsetView):
    """
    A view for displaying a form, and rendering a template response.
    """