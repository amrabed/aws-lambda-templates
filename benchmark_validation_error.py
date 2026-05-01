import json
import timeit

from pydantic import BaseModel, Field, ValidationError


class Item(BaseModel):
    id: str
    name: str


def benchmark_baseline():
    try:
        Item.model_validate_json('{"id": 123}')  # Missing name, wrong type for id
    except ValidationError as exc:
        # Current implementation
        _ = json.loads(exc.json())


def benchmark_optimized():
    try:
        Item.model_validate_json('{"id": 123}')
    except ValidationError as exc:
        # Optimized implementation
        _ = exc.errors()


if __name__ == "__main__":
    n = 10000
    baseline_time = timeit.timeit(benchmark_baseline, number=n)
    optimized_time = timeit.timeit(benchmark_optimized, number=n)

    print(f"Baseline: {baseline_time:.4f}s for {n} iterations")
    print(f"Optimized: {optimized_time:.4f}s for {n} iterations")
    print(f"Improvement: {(baseline_time - optimized_time) / baseline_time * 100:.2f}%")
