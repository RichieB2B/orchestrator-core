# Copyright 2019-2020 SURF, GÉANT.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from ipaddress import IPv4Address, IPv6Address
from uuid import UUID

from pydantic import ConfigDict
from structlog import get_logger

from orchestrator.forms.validators import CustomerId
from orchestrator.types import SubscriptionLifecycle
from orchestrator.workflow import StepList, begin, done, step, workflow
from orchestrator.workflows.steps import store_process_subscription
from orchestrator.workflows.utils import wrap_create_initial_input_form
from pydantic_forms.core import FormPage
from pydantic_forms.types import FormGenerator, State, UUIDstr
from test_orchestrator.products.test_product import TestProductInactive

logger = get_logger(__name__)


def initial_input_form_generator(product_name: str, product: UUIDstr) -> FormGenerator:
    class CreateTestProductForm(FormPage):
        model_config = ConfigDict(title=product_name)

        customer_id: CustomerId

        an_int: int
        a_str: str
        a_bool: bool
        an_uuid: UUIDstr
        an_ipv4: IPv4Address
        an_ipv6: IPv6Address

    user_input = yield CreateTestProductForm

    return user_input.model_dump()


@step("Construct Subscription model")
def construct_subscription_model(
    product: UUIDstr,
    customer_id: UUIDstr,
    an_int: int,
    a_str: str,
    a_bool: bool,
    an_uuid: UUIDstr,
    an_ipv4: IPv4Address,
    an_ipv6: IPv6Address,
) -> State:
    test_product = TestProductInactive.from_product_id(
        product_id=product,
        customer_id=customer_id,
        status=SubscriptionLifecycle.INITIAL,
    )
    test_product.testproduct.an_int = an_int
    test_product.testproduct.a_str = a_str
    test_product.testproduct.a_bool = a_bool
    test_product.testproduct.an_uuid = UUID(an_uuid)
    test_product.testproduct.an_ipv4 = an_ipv4
    test_product.testproduct.an_ipv6 = an_ipv6
    test_product.save()
    return {
        "subscription": test_product,
        "subscription_id": test_product.subscription_id,
        "subscription_description": test_product.description,
    }


@workflow("Create a test product", initial_input_form=wrap_create_initial_input_form(initial_input_form_generator))
def create_test_product() -> StepList:
    return begin >> construct_subscription_model >> store_process_subscription() >> done
