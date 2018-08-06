from django.test import TestCase

# Create your tests here.
def test(request):

    for role in request.user.role.all():
        print(role)