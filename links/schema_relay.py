import graphene
import django_filters
from graphene_django import DjangoObjectType
from graphenne_django.filter import DjangoFilterConnectionField
from .models import Link, Vote

# Relay uses django-filter to filter data
class LinkFilter(django_filters.FilterSet):
  class Meta:
    model = Link
    fields = ['url', 'desription']

# Data is exposed is Nodes so we create one for links
class LinkNode(DjangoObjectType):
  class Meta:
    model = Link
    # Each node implements an interface with a unique ID
    interfaces = (graphene.relay.Node, )

class VoteNode(DjangoObjectType):
  class Meta:
    model = Vote
    interfaces = (graphene.relay.Node, )

class RelayQuery(graphene.ObjectType):
  # Uses LinkNode with relay_link
  relay_link = graphene.relay.Node.Field(LinkNode)
  # Defines the relay_links field as a Connection, to implement pagination
  relay_links = DjangoFilterConnectionField(LinkNode, filterset_class=LinkFilter)

class RelayCreateLink(graphene.relay.ClientIDMutation):
    link = graphene.Field(LinkNode)

    class Input:
        url = graphene.String()
        description = graphene.String()

    def mutate_and_get_payload(root, info, **input):
        user = info.context.user or None

        link = Link(
            url=input.get('url'),
            description=input.get('description'),
            posted_by=user,
        )
        link.save()

        return RelayCreateLink(link=link)


class RelayMutation(graphene.AbstractType):
    relay_create_link = RelayCreateLink.Field()