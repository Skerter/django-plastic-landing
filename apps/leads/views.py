from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from .forms import LeadForm
from .tasks import schedule_lead_notifications


@ratelimit(key="ip", rate="5/h", method="POST", block=False)
def lead_form(request):
    """Обработать форму заявки (HTMX), вернуть HTML-фрагмент для свапа.

    Поведение по методу:

    * **GET** — пустая форма (используется как include на страницах).
    * **POST, валидна** — сохраняет ``Lead``, ставит уведомления в очередь,
      возвращает фрагмент «спасибо» (200).
    * **POST, ошибки валидации** — фрагмент полей с подсветкой ошибок (200).
    * **Превышен лимит** (5/час с IP) — фрагмент с предложением позвонить (429).

    Заявка всегда пишется в БД первой; рассылка по каналам идёт асинхронно и
    ответ её не ждёт.
    """
    if getattr(request, "limited", False):
        # 429 — корректный статус. htmx настроен свапать 4xx (см. base.html,
        # htmx-config → responseHandling), поэтому фрагмент покажется.
        html = render_to_string("leads/ratelimit.html", request=request)
        return HttpResponse(html, status=429)

    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.consent = True
            lead.save()
            schedule_lead_notifications(lead.id)
            html = render_to_string("leads/success.html", request=request)
            return HttpResponse(html)
        # ошибки валидации — возвращаем только свапаемый фрагмент полей
        html = render_to_string(
            "leads/form_fields.html", {"form": form}, request=request
        )
        return HttpResponse(html, status=200)

    # GET — пустая форма (используется как include на страницах)
    return render(request, "leads/form.html", {"form": LeadForm()})
