from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from .forms import LeadForm
from .tasks import schedule_lead_notifications


@ratelimit(key="ip", rate="5/h", method="POST", block=False)
def lead_form(request):
    """Handle the lead form (HTMX) and return an HTML fragment to swap in.

    Behaviour by method:

    * **GET** — an empty form (used as an include on pages).
    * **POST, valid** — saves the ``Lead``, queues the notifications and returns
      the "thank you" fragment (200).
    * **POST, validation errors** — the fields fragment with errors highlighted (200).
    * **Rate limit exceeded** (5/hour per IP) — a fragment offering a phone call (429).

    The lead is always written to the database first; the channel fan-out is
    asynchronous and the response does not wait for it.
    """
    if getattr(request, "limited", False):
        # 429 is the correct status here. htmx is configured to swap 4xx
        # (see base.html, htmx-config → responseHandling), so the fragment shows up.
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
        # validation errors — return only the swappable fields fragment
        html = render_to_string(
            "leads/form_fields.html", {"form": form}, request=request
        )
        return HttpResponse(html, status=200)

    # GET — an empty form (used as an include on pages)
    return render(request, "leads/form.html", {"form": LeadForm()})
