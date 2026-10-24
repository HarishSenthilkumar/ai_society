import random
import time

from society import Society


def main():

    random.seed()

    population = 100

    society = Society(
        population=population,
        width=30,
        height=30
    )

    print(
        "Starting AI Society..."
    )

    time.sleep(1)

    society.run(
        days=5000,
        delay=0.01,
        display_every=25
    )

    society.save(
        "society_save.json"
    )

    print()

    print(
        "Simulation complete."
    )

    print(
        "Saved to society_save.json"
    )


if __name__ == "__main__":

    main()
