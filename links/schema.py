import graphene
from graphene_django import DjangoObjectType

from .models import Link


class LinkType(DjangoObjectType):
    class Meta:
        model = Link


class Query(graphene.ObjectType):
    links = graphene.List(LinkType)

    def resolve_links(self, info, **kwargs):
        return Link.objects.all()

# defines a mutation class
class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()

    # defines data that can be sent to server, ie url and description
    class Arguments:
        url = graphene.String()
        description = graphene.String()

    # Mutation method: creates a link on database using url and description, 
    # and server returns CreateLink class with data
    def mutate(self, info, url, description):
        link = Link(url=url, description=description)
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description
        )

# Creates a mutation class with a field to be resolved, pointing to previously defined mutation
class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()