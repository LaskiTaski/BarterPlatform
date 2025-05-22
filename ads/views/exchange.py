from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from ..models import ExchangeProposal, Ad
from ..forms import ExchangeProposalForm


class ExchangeProposalCreateView(LoginRequiredMixin, CreateView):
    model = ExchangeProposal
    form_class = ExchangeProposalForm
    template_name = 'ads/exchangeproposal_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ad_receiver'] = get_object_or_404(Ad, pk=self.kwargs['ad_receiver_pk'])
        return context

    def form_valid(self, form):
        ad_receiver = get_object_or_404(Ad, pk=self.kwargs['ad_receiver_pk'])
        form.instance.ad_receiver = ad_receiver
        form.instance.status = 'pending'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.kwargs['ad_receiver_pk']})


class ExchangeProposalAcceptView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)

        # Меняем владельцев местами (Не стал выносить в отдельный метод т.к это разовое решение, если делать хорошо, то
        # нужно вынести эту часть в отдельный метод и желательно файл, если часто придётся это использовать)
        ad_sender = proposal.ad_sender
        ad_receiver = proposal.ad_receiver
        user_sender = ad_sender.user
        user_receiver = ad_receiver.user
        ad_sender.user, ad_receiver.user = user_receiver, user_sender
        ad_sender.save()
        ad_receiver.save()

        # Обновляем статус
        proposal.status = 'accepted'
        proposal.save()
        messages.success(request, "Обмен успешно совершен!")
        return redirect('ads:ad_detail', pk=proposal.ad_receiver.pk)

    def test_func(self):
        proposal = get_object_or_404(ExchangeProposal, pk=self.kwargs['pk'])
        return proposal.ad_receiver.user == self.request.user


class ExchangeProposalDeclineView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        proposal = get_object_or_404(ExchangeProposal, pk=pk)
        proposal.status = 'declined'
        proposal.save()
        messages.info(request, "Предложение отклонено.")
        return redirect('ads:ad_detail', pk=proposal.ad_receiver.pk)

    def test_func(self):
        proposal = get_object_or_404(ExchangeProposal, pk=self.kwargs['pk'])
        return proposal.ad_receiver.user == self.request.user


class MyExchangeProposalsView(LoginRequiredMixin, ListView):
    model = ExchangeProposal
    template_name = "ads/my_exchange_proposals.html"
    context_object_name = "proposals"

    def get_queryset(self):
        return ExchangeProposal.objects.filter(ad_receiver__user=self.request.user).select_related("ad_sender",
                                                                                                   "ad_receiver")
