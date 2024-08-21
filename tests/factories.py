import factory
import factory.fuzzy
from faker import Faker

from madr.models import Livro, Romancista, User
from madr.security import get_password_hash
from madr.utils import sanitize

faker = Faker()


class UserFactory(factory.Factory[User]):
    class Meta:
        model = User
        exclude = ('clean_password',)

    email = factory.LazyFunction(faker.email)
    username = factory.LazyFunction(lambda: sanitize(faker.user_name()))
    password = factory.LazyAttribute(lambda obj: get_password_hash(obj.clean_password))
    clean_password = factory.LazyAttribute(faker.password)


class RomancistaFactory(factory.Factory[Romancista]):
    class Meta:
        model = Romancista

    name = factory.LazyFunction(lambda: sanitize(faker.name()))


class LivroFactory(factory.Factory[Livro]):
    class Meta:
        model = Livro

    title = factory.LazyFunction(lambda: sanitize(faker.text(40)))
    year = factory.fuzzy.FuzzyInteger(1900, 2100)
    romancista = factory.SubFactory(RomancistaFactory)
