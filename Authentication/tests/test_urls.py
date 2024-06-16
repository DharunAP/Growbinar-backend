
# for testing always start the function name with test

from django.test import SimpleTestCase
from Authentication.views import *
from Authentication.urls import *
from django.urls import reverse,resolve 

class basicTesting(SimpleTestCase) :

    def test_first(self):
        url = reverse('login-route')
        print(resolve(url))
        self.assertEquals(resolve(url).func,user_login)