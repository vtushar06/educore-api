from django.shortcuts import render


def api_root_landing(request):
    """
    Renders the beautiful glassmorphism API root landing page.
    """
    return render(request, "landing.html")
