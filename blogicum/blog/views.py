from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .forms import PostForm, CommentForm
from .models import Category, Post, Comment


POSTS_PER_PAGE = 10


def index(request):
    post_list = (
        Post.objects.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
        .select_related('category', 'location', 'author')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    post = get_object_or_404(
        Post,
        id=id,
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )

    comments = post.comments.select_related('author').order_by('created_at')
    form = CommentForm()  # шаблон сам решит показывать/не показывать

    return render(
        request,
        'blog/detail.html',
        {'post': post, 'comments': comments, 'form': form},
    )


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)

    post_list = (
        category.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
        )
        .select_related('category', 'location', 'author')
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {'category': category, 'page_obj': page_obj})


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            request.FILES,
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(
                'blog:profile',
                username=request.user.username,
            )
    else:
        form = PostForm()

    return render(
        request,
        'blog/create.html',
        {'form': form},
    )

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect('blog:post_detail', id=post_id)

@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/create.html', {'form': form, 'post': post})

@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)

    form = CommentForm(instance=comment)
    post = comment.post
    comments = post.comments.select_related('author').order_by('created_at')

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'form': form,
            'comments': comments,
            'editing_comment': comment,
        },
    )

@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    post = comment.post
    comments = post.comments.select_related('author').order_by('created_at')

    return render(
        request,
        'blog/detail.html',
        {
            'post': post,
            'comments': comments,
            'comment_to_delete': comment,
        },
    )

@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect(
            'blog:profile',
            username=request.user.username,
        )

    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})