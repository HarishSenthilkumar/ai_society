import random
from config import JOBS, PERSONALITIES


class Agent:

    next_id = 1

    def __init__(self, world):

        self.id = Agent.next_id
        Agent.next_id += 1

        self.name = f"Agent_{self.id:03d}"

        self.world = world

        self.age = random.randint(18, 65)
        self.gender = random.choice(["male", "female"])

        self.job = random.choice(list(JOBS.keys()))

        self.money = round(random.uniform(40, 180), 2)
        self.food = random.randint(1, 5)

        self.energy = random.uniform(60, 100)
        self.hunger = random.uniform(0, 30)
        self.health = random.uniform(70, 100)
        self.social = random.uniform(30, 100)
        self.happiness = random.uniform(50, 90)

        self.personality = random.choice(PERSONALITIES)

        self.ambition = random.random()
        self.sociability = random.random()
        self.generosity = random.random()
        self.aggression = random.random()

        self.x = random.randrange(world.width)
        self.y = random.randrange(world.height)

        self.partner = None
        self.children = []
        self.parents = []

        self.alive = True

        self.memory = []
        self.last_action = "created"

        self.age_ticks = 0

    @property
    def location(self):

        return self.world.locations.get(
            (self.x, self.y),
            "wilderness"
        )

    def distance(self, other):

        return (
            abs(self.x - other.x)
            +
            abs(self.y - other.y)
        )

    def move_toward(self, x, y):

        if self.x < x:
            self.x += 1

        elif self.x > x:
            self.x -= 1

        elif self.y < y:
            self.y += 1

        elif self.y > y:
            self.y -= 1

    def move_random(self):

        direction = random.choice([
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1)
        ])

        self.x += direction[0]
        self.y += direction[1]

        self.x = max(
            0,
            min(self.world.width - 1, self.x)
        )

        self.y = max(
            0,
            min(self.world.height - 1, self.y)
        )

    def add_memory(self, memory):

        self.memory.append(memory)

        if len(self.memory) > 20:
            self.memory.pop(0)

    def utility(self, action):

        if action == "eat":

            return self.hunger * 3

        if action == "sleep":

            return (100 - self.energy) * 2.2

        if action == "work":

            score = (
                self.ambition * 40
                +
                max(0, 100 - self.money) * 0.25
            )

            if self.job == "unemployed":
                score *= 0.5

            return score

        if action == "socialize":

            return (
                (100 - self.social)
                *
                (1 + self.sociability * 2)
            )

        if action == "shop":

            return (
                self.hunger * 1.5
                +
                max(0, 70 - self.food) * 2
            )

        if action == "rest":

            return (
                (100 - self.health) * 1.5
                +
                (100 - self.energy) * 0.5
            )

        if action == "wander":

            return 15 + self.sociability * 10

        if action == "find_partner":

            if self.partner is not None:
                return 0

            if self.age < 20 or self.age > 55:
                return 0

            return (
                self.sociability * 25
                +
                self.happiness * 0.2
            )

        return 0

    def choose_action(self):

        actions = [
            "eat",
            "sleep",
            "work",
            "socialize",
            "shop",
            "rest",
            "wander",
            "find_partner"
        ]

        scores = {}

        for action in actions:

            scores[action] = (
                self.utility(action)
                +
                random.uniform(0, 8)
            )

        return max(
            scores,
            key=scores.get
        )

    def act(self):

        action = self.choose_action()

        self.last_action = action

        if action == "eat":
            self.eat()

        elif action == "sleep":
            self.sleep()

        elif action == "work":
            self.work()

        elif action == "socialize":
            self.socialize()

        elif action == "shop":
            self.shop()

        elif action == "rest":
            self.rest()

        elif action == "wander":
            self.move_random()

        elif action == "find_partner":
            self.find_partner()

    def eat(self):

        if self.food > 0:

            self.food -= 1

            self.hunger = max(
                0,
                self.hunger - 35
            )

            self.health = min(
                100,
                self.health + 1
            )

            self.happiness = min(
                100,
                self.happiness + 2
            )

            self.add_memory(
                "Ate food."
            )

        else:

            self.hunger = min(
                100,
                self.hunger + 8
            )

            self.happiness = max(
                0,
                self.happiness - 5
            )

    def sleep(self):

        self.energy = min(
            100,
            self.energy + 25
        )

        self.health = min(
            100,
            self.health + 2
        )

        self.hunger = min(
            100,
            self.hunger + 4
        )

        self.social = max(
            0,
            self.social - 2
        )

        self.add_memory(
            "Slept."
        )

    def work(self):

        job = JOBS[self.job]

        income = (
            job["income"]
            *
            self.world.economy_multiplier
        )

        income *= random.uniform(
            0.8,
            1.2
        )

        if self.hunger > 80:
            income *= 0.5

        if self.energy < 20:
            income *= 0.5

        if self.health < 30:
            income *= 0.4

        self.money += income

        self.energy = max(
            0,
            self.energy - random.uniform(8, 15)
        )

        self.hunger = min(
            100,
            self.hunger + random.uniform(4, 9)
        )

        self.social = max(
            0,
            self.social - 2
        )

        self.happiness = min(
            100,
            self.happiness
            +
            (2 if self.money > 100 else -1)
        )

        self.world.production += job["production"]

        self.world.food_produced += job["food"]

        self.add_memory(
            f"Worked as {self.job}."
        )

    def shop(self):

        if self.food <= 0:
            amount = 2
        else:
            amount = 1

        price = (
            self.world.food_price
            *
            amount
        )

        if self.money >= price:

            self.money -= price

            self.food += amount

            self.happiness = min(
                100,
                self.happiness + 2
            )

            self.world.food_sold += amount

            self.add_memory(
                f"Bought {amount} food."
            )

        else:

            self.happiness = max(
                0,
                self.happiness - 3
            )

    def socialize(self):

        candidates = [
            agent
            for agent in self.world.agents
            if agent.alive
            and agent.id != self.id
            and self.distance(agent) <= 4
        ]

        if not candidates:

            self.move_random()

            return

        other = random.choice(
            candidates
        )

        amount = random.uniform(
            5,
            15
        )

        self.social = min(
            100,
            self.social + amount
        )

        other.social = min(
            100,
            other.social + amount * 0.7
        )

        compatibility = (
            1
            -
            abs(
                self.sociability
                -
                other.sociability
            )
        )

        change = (
            random.uniform(1, 5)
            *
            compatibility
        )

        self.happiness = min(
            100,
            self.happiness + change
        )

        other.happiness = min(
            100,
            other.happiness + change
        )

        key = (
            min(self.id, other.id),
            max(self.id, other.id)
        )

        self.world.relations[key] += change

        self.add_memory(
            f"Talked with {other.name}."
        )

        other.add_memory(
            f"Talked with {self.name}."
        )

    def rest(self):

        self.energy = min(
            100,
            self.energy + 8
        )

        self.health = min(
            100,
            self.health + 5
        )

        self.happiness = min(
            100,
            self.happiness + 1
        )

    def find_partner(self):

        if self.partner is not None:
            return

        candidates = [
            agent
            for agent in self.world.agents
            if agent.alive
            and agent.id != self.id
            and agent.partner is None
            and 20 <= agent.age <= 55
            and agent.gender != self.gender
            and self.distance(agent) <= 5
        ]

        if not candidates:

            self.move_random()

            return

        other = min(
            candidates,
            key=lambda agent:
            abs(
                agent.sociability
                -
                self.sociability
            )
        )

        compatibility = (
            (
                1
                -
                abs(
                    self.sociability
                    -
                    other.sociability
                )
            )
            +
            (
                1
                -
                abs(
                    self.ambition
                    -
                    other.ambition
                )
            )
            +
            (
                1
                -
                abs(
                    self.generosity
                    -
                    other.generosity
                )
            )
        ) / 3

        if (
            compatibility > 0.65
            and random.random() < 0.35
        ):

            self.partner = other
            other.partner = self

            self.happiness = min(
                100,
                self.happiness + 15
            )

            other.happiness = min(
                100,
                other.happiness + 15
            )

            self.add_memory(
                f"Started relationship with {other.name}."
            )

            other.add_memory(
                f"Started relationship with {self.name}."
            )

    def age_tick(self):

        self.age_ticks += 1

        self.hunger = min(
            100,
            self.hunger + random.uniform(1, 3)
        )

        self.energy = max(
            0,
            self.energy - random.uniform(1, 4)
        )

        self.social = max(
            0,
            self.social - random.uniform(0, 2)
        )

        if self.hunger > 85:

            self.health -= 2

            self.happiness -= 2

        if self.energy < 10:

            self.health -= 1

        if self.age > 70:

            self.health -= random.uniform(
                0,
                2
            )

        if self.health <= 0:

            self.die()

    def die(self):

        if not self.alive:
            return

        self.alive = False

        self.world.deaths += 1

        self.world.log_event(
            f"{self.name} died at age {self.age}."
        )

        if self.partner is not None:

            self.partner.partner = None

            self.partner.happiness = max(
                0,
                self.partner.happiness - 20
            )

            self.partner = None

        for child in self.children:

            child.happiness = max(
                0,
                child.happiness - 5
            )
