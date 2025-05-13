from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from .models import Article, Comment, ArticleCategory
from .forms import CommentForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class ArticleList(ListView):
    model = Article
    template_name = 'wiki_list.html'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Article.objects.exclude(author=self.request.user.profile)
        return Article.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        categories = ArticleCategory.objects.all()

        articles_by_category = []
        for category in categories:
            if user.is_authenticated:
                articles = category.articles.exclude(author=user.profile)
            else:
                articles = category.articles.all()

            if articles.exists():
                  articles_by_category.append((category, articles))
        context['articles_by_category'] = articles_by_category
 
        if self.request.user.is_authenticated:
            context['user_articles'] = Article.objects.filter(author=user.profile)
             
        return context

class ArticleDetail(DetailView):
    model = Article
    template_name = 'wiki_detail.html'

    def get_queryset(self):
        return Article.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        category = article.category

        context['other_articles'] = Article.objects.filter(category=category).exclude(pk=article.pk)[:2]
        context['comments'] = Comment.objects.filter(article=article).order_by('-created_on')
        context['comment_form'] = CommentForm
        
        if self.request.user.is_authenticated and self.request.user.profile == article.author:
            context['edit_link'] = reverse_lazy('article_edit', args=[article.pk])

        return context

class ArticleCreate(LoginRequiredMixin, CreateView):
    model = Article
    template_name = 'wiki_create.html'
    fields = ['title', 'category', 'entry', 'header_image']

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        return super().form_valid(form)
    
    def get_success_url(self):
        return super().get_success_url()
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class ArticleUpdate(LoginRequiredMixin, UpdateView):
    model = Article
    template_name = 'wiki_update.html'
    fields = ['title', 'category', 'entry', 'header_image']

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('article_detail', kwargs={'pk':self.get_object().pk})