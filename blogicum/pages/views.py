from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count
from django.views.generic import TemplateView

from blog.models import Post

User = get_user_model()
POSTS_PER_PAGE = 10


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/registration_form.html',
        {'form': form},
    )


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=user_profile)

    if request.user != user_profile:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )

    posts = posts.select_related('category', 'location').order_by('-pub_date')
    posts = posts.select_related('category', 'location').annotate(comment_count=Count('comments')).order_by('-pub_date')

    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile_user': user_profile,
        'page_obj': page_obj,
    }
    return render(request, 'pages/profile.html', context)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)

class AboutView(TemplateView):
    template_name = 'pages/about.html'

class RulesView(TemplateView):
    template_name = 'pages/rules.html'
