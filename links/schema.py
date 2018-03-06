import graphene
from graphene_django import DjangoObjectType

from links.models import Link, Vote
from users.schema import UserType
from graphql import GraphQLError
from django.db.models import Q


class LinkType(DjangoObjectType):
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    # Add the search parameter inside our links field
    links = graphene.List(LinkType, search=graphene.String())
    votes = graphene.List(VoteType)

    # Change the resolver
    def resolve_links(self, info, search=None, **kwargs):
        # The value sent with the search parameter will be on the args variable
        if search:
            filter = (
                Q(url__icontains=search) | 
                Q(description__icontains=search)
            )
            return Link.objects.filter(filter)

        return Link.objects.all()

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()

# defines a mutation class
class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    # defines data that can be sent to server, ie url and description
    class Arguments:
        url = graphene.String()
        description = graphene.String()

    # Mutation method: creates a link on database using url and description, 
    # and server returns CreateLink class with data
    def mutate(self, info, url, description):
        user = info.context.user or None

        link = Link(
            url=url,
            description=description,
            posted_by=user
        )
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by
        )

class CreateVote(graphene.mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            # standard Py errorhandling
            raise Exception('You must be logged in to vote!')
        
        link = Link.objects.filter(id-link_id).first()
        if not link:
            # handling errors via GraphQLError -- graphql is strongly typed and can determine incorrec values immediately
            raise GraphQLError('Invalid Link!')

        Vote.objects.create(
            user=user,
            link=link
        )

        return CreateVote(user=user, link=link)
# Creates a mutation class with a field to be resolved, pointing to previously defined mutation
class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()