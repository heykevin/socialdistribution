from rest_framework.response import Response
from rest_framework import generics, viewsets, mixins
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from models import Post, Comment
from serializers import PostSerializer, CommentSerializer
from permissions import IsAuthor, Custom
from author_api.models import Author
from author_api.serializers import AuthorSerializer
from renderers import PostsJSONRenderer
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
#
# Delete Posts and Comments
#

class BaseDeleteView(generics.DestroyAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsAuthor,)
    pass

class DeleteComment(BaseDeleteView):
    lookup_url_kwarg = "commentid"

    def get_queryset(self):
        return Comment.objects.filter(guid = self.kwargs.get(
            self.lookup_url_kwarg))

#
# Create Post and Comments
#
class CreateComment(generics.CreateAPIView):
    """
    Create a comment in the given post using postid.
    Can only create comments on posts you have permission to view.
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, Custom,)
    serializer_class = CommentSerializer
    lookup_url_kwarg = "postid"

    def get_serializer_context(self):
        """
        Provide the serializer_class with Post model context needed to create a Comment
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'post': Post.objects.get(guid = self.kwargs.get(self.lookup_url_kwarg))
        }

#
# Post Retrieval for authors and timeline
#
class PostBaseView(object):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class AuthorPostViewSet(
    PostBaseView,
    viewsets.ViewSet
):
    # authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [Custom]

    """
    Returns a listing of posts for the given author ID

    Takes:
        id: The uuid of an author model.
    """
    def list(self, request, author_pk=None):
        posts = self.queryset.filter(author__id=author_pk)
        guids = []
        for post in posts:
            # We still want to return posts, but only those that we have permissions
            # for
            try:
                self.check_object_permissions(self.request, post)
            except Exception:
                guids.append(post.guid)

        serializer = PostSerializer(posts.exclude(guid__in=guids), many=True)
        return Response({"posts": serializer.data})

    def retrieve(self, request, author_pk=None, pk=None):
        # Careful, gotchya here, if author_pk is none, it means we are dealing with
        # /author/:id and that the author id is going to be in pk
        if author_pk is None:
            author = get_object_or_404(Author.objects.all(), id=pk)
            serializer = AuthorSerializer(author)
        else:
            post = self.queryset.get(author__id=author_pk, guid=pk)
            self.check_object_permissions(self.request, post)
            serializer = PostSerializer(post)

        return Response(serializer.data)

    # TIMELINE call
    @list_route(methods=['get'], permission_classes=[IsAuthenticated, IsAuthor])
    def posts(self, request):
        user = self.request.user
        # TODO: filter by author id and following ids as well
        # author = Author.objects.get(user__id=user.id)
        # followers = author.followers
        queryset = Post.objects.all().filter(author__user__id=user.id)
        serializer = PostSerializer(queryset, many=True)
        return Response({"posts": serializer.data})


# Handles all interactions with post objects
class PostViewSet(
  PostBaseView,
  mixins.CreateModelMixin,
  mixins.RetrieveModelMixin,
  mixins.UpdateModelMixin,
  mixins.DestroyModelMixin,
  viewsets.GenericViewSet
):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, Custom]
    parser_classes = (MultiPartParser, FormParser, JSONParser)


class PublicPostsViewSet(
    PostBaseView,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    renderer_classes = (PostsJSONRenderer,)

    def get_queryset(self):
        return self.queryset.filter(visibility="PUBLIC")
