from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm

from django.contrib.auth.forms import UserCreationForm


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def ad_list(request):
    ads = Ad.objects.all().order_by('-created_at')
    return render(request, 'ads/ad_list.html', {'ads': ads})


def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    proposals = ExchangeProposal.objects.filter(ad_receiver=ad)
    return render(request, 'ads/ad_detail.html', {'ad': ad, 'proposals': proposals})


@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm()
    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def ad_update(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        return redirect('ad_list')
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            return redirect('ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/ad_form.html', {'form': form})


@login_required
def ad_delete(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if ad.user != request.user:
        return redirect('ad_list')
    if request.method == 'POST':
        ad.delete()
        return redirect('ad_list')
    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
def exchangeproposal_create(request, ad_receiver_pk):
    ad_receiver = get_object_or_404(Ad, pk=ad_receiver_pk)
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad_receiver
            proposal.status = 'pending'
            proposal.save()
            return redirect('ad_detail', pk=ad_receiver.pk)
    else:
        form = ExchangeProposalForm(user=request.user)
    return render(request, 'ads/exchangeproposal_form.html', {'form': form, 'ad_receiver': ad_receiver})


@login_required
def my_exchange_proposals(request):
    proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user).select_related('ad_sender',
                                                                                               'ad_receiver')
    return render(request, 'ads/my_exchange_proposals.html', {'proposals': proposals})


@login_required
def exchangeproposal_accept(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    # Проверяем, что пользователь — владелец объявления-получателя
    if proposal.ad_receiver.user != request.user or proposal.status != 'pending':
        messages.error(request, "У вас нет прав на это действие или предложение уже обработано.")
        return redirect('ad_detail', pk=proposal.ad_receiver.pk)
    # Меняем владельцев местами
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
    return redirect('ad_detail', pk=ad_receiver.pk)


@login_required
def exchangeproposal_decline(request, pk):
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    if proposal.ad_receiver.user != request.user or proposal.status != 'pending':
        messages.error(request, "У вас нет прав на это действие или предложение уже обработано.")
        return redirect('ad_detail', pk=proposal.ad_receiver.pk)
    proposal.status = 'declined'
    proposal.save()
    messages.info(request, "Предложение отклонено.")
    return redirect('ad_detail', pk=proposal.ad_receiver.pk)
