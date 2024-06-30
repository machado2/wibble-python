import random

from app.models import Examples


async def get_examples() -> list[tuple[str, str]]:
    # Step 1: Get the maximum new_id
    max_id_example = await Examples.all().order_by("-new_id").first()
    max_id = max_id_example.new_id if max_id_example else None

    if max_id is not None:
        # Step 2: Generate random new_id values
        random_ids = random.sample(range(1, max_id + 1), 3)

        # Step 3: Fetch rows based on random new_id values
        examples = await Examples.filter(new_id__in=random_ids).all()

        # Process the results
        return [(example.user_input, example.content) for example in examples if example.content]
    else:
        # Handle the case where the table is empty
        return []
