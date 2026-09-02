import random
import time
import json
from collections import defaultdict, Counter


JOBS = {
    "farmer": {
        "income": 8,
        "food": 5,
        "production": 4
    },
    "miner": {
        "income": 12,
        "food": 0,
        "production": 3
    },
    "builder": {
        "income": 15,
        "food": 0,
        "production": 1
    },
    "merchant": {
        "income": 11,
        "food": 1,
        "production": 1
    },
    "doctor": {
        "income": 20,
        "food": 0,
        "production": 0
    },
    "teacher": {
        "income": 14,
        "food": 1,
        "production": 0
    },
    "engineer": {
        "income": 22,
        "food": 0,
        "production": 2
    },
    "artist": {
        "income": 9,
        "food": 1,
        "production": 0
    },
    "unemployed": {
        "income": 3,
        "food": 0,
        "production": 0
    }
}

PERSONALITIES = [
    "ambitious",
    "generous",
    "social",
    "aggressive",
    "cautious",
    "balanced"
]


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


class Society:

    def __init__(
        self,
        population=100,
        width=30,
        height=30
    ):

        self.width = width
        self.height = height

        self.day = 0

        self.agents = []

        self.relations = defaultdict(float)

        self.food_price = 5.0

        self.economy_multiplier = 1.0

        self.production = 0

        self.food_produced = 0

        self.food_sold = 0

        self.births = 0

        self.deaths = 0

        self.history = []

        self.event_log = []

        self.locations = {}

        self.setup_world()

        for _ in range(population):

            self.agents.append(
                Agent(self)
            )

        self.create_initial_families()

    def setup_world(self):

        locations = [
            "farm",
            "farm",
            "farm",
            "market",
            "market",
            "factory",
            "hospital",
            "school",
            "bank",
            "park",
            "factory",
            "house",
            "house",
            "house"
        ]

        for location in locations:

            x = random.randrange(
                self.width
            )

            y = random.randrange(
                self.height
            )

            self.locations[
                (x, y)
            ] = location

    def create_initial_families(self):

        eligible = [
            agent
            for agent in self.agents
            if 25 <= agent.age <= 45
        ]

        random.shuffle(
            eligible
        )

        for i in range(
            0,
            len(eligible) - 1,
            2
        ):

            a = eligible[i]

            b = eligible[i + 1]

            if (
                a.partner is None
                and
                b.partner is None
                and
                random.random() < 0.25
            ):

                a.partner = b
                b.partner = a

    def alive_agents(self):

        return [
            agent
            for agent in self.agents
            if agent.alive
        ]

    def log_event(self, event):

        entry = (
            f"Day {self.day}: {event}"
        )

        self.event_log.append(
            entry
        )

        if len(self.event_log) > 1000:

            self.event_log.pop(0)

    def update_economy(self):

        alive = self.alive_agents()

        if not alive:
            return

        total_food = sum(
            agent.food
            for agent in alive
        )

        demand = sum(
            1 + agent.hunger / 100
            for agent in alive
        )

        if total_food <= 0:

            self.food_price *= 1.12

        else:

            ratio = (
                demand
                /
                total_food
            )

            self.food_price *= (
                1
                +
                max(
                    -0.05,
                    min(
                        0.08,
                        (ratio - 0.5) * 0.1
                    )
                )
            )

        self.food_price = max(
            1,
            min(
                30,
                self.food_price
            )
        )

        avg_health = (
            sum(
                agent.health
                for agent in alive
            )
            /
            len(alive)
        )

        avg_happiness = (
            sum(
                agent.happiness
                for agent in alive
            )
            /
            len(alive)
        )

        self.economy_multiplier = (
            0.9
            +
            avg_health / 500
            +
            avg_happiness / 1000
        )

    def handle_health(self):

        for agent in self.alive_agents():

            if agent.location == "hospital":

                agent.health = min(
                    100,
                    agent.health + 8
                )

    def handle_births(self):

        couples = []

        for agent in self.alive_agents():

            if agent.partner is None:
                continue

            if agent.gender != "female":
                continue

            partner = agent.partner

            if not partner.alive:
                continue

            if not 20 <= agent.age <= 45:
                continue

            if not 20 <= partner.age <= 55:
                continue

            if agent.money + partner.money < 80:
                continue

            if random.random() < 0.004:

                couples.append(
                    (agent, partner)
                )

        for mother, father in couples:

            if len(self.alive_agents()) >= 300:
                break

            child = Agent(self)

            child.age = 0

            child.gender = random.choice(
                ["male", "female"]
            )

            child.job = "unemployed"

            child.money = 0

            child.food = 0

            child.energy = 100

            child.hunger = 20

            child.health = random.uniform(
                75,
                100
            )

            child.social = 70

            child.happiness = 75

            child.x = mother.x
            child.y = mother.y

            child.parents = [
                mother,
                father
            ]

            mother.children.append(
                child
            )

            father.children.append(
                child
            )

            self.agents.append(
                child
            )

            self.births += 1

            mother.happiness = min(
                100,
                mother.happiness + 10
            )

            father.happiness = min(
                100,
                father.happiness + 10
            )

            self.log_event(
                f"{mother.name} and {father.name} had {child.name}."
            )

    def random_event(self):

        if random.random() > 0.03:
            return

        event = random.choice([
            "drought",
            "economic_boom",
            "factory_accident",
            "festival",
            "disease",
            "food_surplus",
            "storm"
        ])

        alive = self.alive_agents()

        if event == "drought":

            for agent in alive:

                if agent.job == "farmer":

                    agent.happiness = max(
                        0,
                        agent.happiness - 8
                    )

                    agent.money = max(
                        0,
                        agent.money - 5
                    )

            self.food_price *= 1.35

            self.log_event(
                "A drought reduced food production."
            )

        elif event == "economic_boom":

            self.economy_multiplier *= 1.25

            for agent in alive:

                agent.happiness = min(
                    100,
                    agent.happiness + 8
                )

                agent.money += random.uniform(
                    5,
                    20
                )

            self.log_event(
                "An economic boom increased wealth."
            )

        elif event == "factory_accident":

            workers = [
                agent
                for agent in alive
                if agent.job in [
                    "miner",
                    "builder",
                    "engineer"
                ]
            ]

            if workers:

                victim = random.choice(
                    workers
                )

                victim.health -= random.uniform(
                    10,
                    30
                )

                victim.happiness = max(
                    0,
                    victim.happiness - 10
                )

                self.log_event(
                    f"{victim.name} was injured."
                )

        elif event == "festival":

            for agent in alive:

                agent.happiness = min(
                    100,
                    agent.happiness
                    +
                    random.uniform(
                        5,
                        15
                    )
                )

                agent.social = min(
                    100,
                    agent.social + 10
                )

            self.log_event(
                "A large festival brought society together."
            )

        elif event == "disease":

            if not alive:
                return

            victims = random.sample(
                alive,
                min(
                    len(alive),
                    max(
                        1,
                        len(alive) // 10
                    )
                )
            )

            for victim in victims:

                victim.health -= random.uniform(
                    5,
                    20
                )

                victim.happiness = max(
                    0,
                    victim.happiness - 5
                )

            self.log_event(
                "A disease outbreak affected society."
            )

        elif event == "food_surplus":

            self.food_price *= 0.8

            for agent in alive:

                if agent.job == "farmer":

                    agent.money += 10

            self.log_event(
                "A food surplus lowered prices."
            )

        elif event == "storm":

            for agent in alive:

                if random.random() < 0.2:

                    agent.health -= random.uniform(
                        2,
                        10
                    )

                    agent.happiness = max(
                        0,
                        agent.happiness - 5
                    )

            self.log_event(
                "A major storm hit the settlement."
            )

    def redistribute_jobs(self):

        unemployed = [
            agent
            for agent in self.alive_agents()
            if agent.job == "unemployed"
        ]

        for agent in unemployed:

            if (
                agent.age >= 16
                and
                random.random() < 0.08
            ):

                available_jobs = [
                    job
                    for job in JOBS
                    if job != "unemployed"
                ]

                agent.job = random.choice(
                    available_jobs
                )

                self.log_event(
                    f"{agent.name} became a {agent.job}."
                )

    def update_relationships(self):

        alive = self.alive_agents()

        for agent in alive:

            nearby = [
                other
                for other in alive
                if (
                    other.id != agent.id
                    and
                    agent.distance(other) <= 3
                )
            ]

            for other in nearby:

                key = (
                    min(agent.id, other.id),
                    max(agent.id, other.id)
                )

                if agent.last_action == "socialize":

                    self.relations[key] += 1

                self.relations[key] *= 0.999

    def daily_update(self):

        self.day += 1

        self.production = 0

        self.food_produced = 0

        self.food_sold = 0

        self.random_event()

        self.redistribute_jobs()

        for agent in list(
            self.alive_agents()
        ):

            if (
                agent.age > 0
                and
                agent.age_ticks >= 365
            ):

                agent.age += 1

                agent.age_ticks = 0

            agent.act()

            agent.age_tick()

        self.handle_health()

        self.handle_births()

        self.update_relationships()

        self.update_economy()

        if self.day % 30 == 0:

            self.monthly_update()

    def monthly_update(self):

        alive = self.alive_agents()

        if not alive:
            return

        self.history.append({

            "day": self.day,

            "population": len(alive),

            "average_happiness":
                sum(
                    agent.happiness
                    for agent in alive
                ) / len(alive),

            "average_health":
                sum(
                    agent.health
                    for agent in alive
                ) / len(alive),

            "wealth":
                sum(
                    agent.money
                    for agent in alive
                ),

            "food_price":
                self.food_price
        })

    def statistics(self):

        alive = self.alive_agents()

        if not alive:
            return {}

        jobs = Counter(
            agent.job
            for agent in alive
        )

        return {

            "day":
                self.day,

            "population":
                len(alive),

            "average_age":
                sum(
                    agent.age
                    for agent in alive
                ) / len(alive),

            "average_happiness":
                sum(
                    agent.happiness
                    for agent in alive
                ) / len(alive),

            "average_health":
                sum(
                    agent.health
                    for agent in alive
                ) / len(alive),

            "average_money":
                sum(
                    agent.money
                    for agent in alive
                ) / len(alive),

            "food_price":
                self.food_price,

            "births":
                self.births,

            "deaths":
                self.deaths,

            "jobs":
                dict(jobs)
        }

    def richest(self, count=5):

        return sorted(
            self.alive_agents(),
            key=lambda agent:
            agent.money,
            reverse=True
        )[:count]

    def happiest(self, count=5):

        return sorted(
            self.alive_agents(),
            key=lambda agent:
            agent.happiness,
            reverse=True
        )[:count]

    def strongest_relationships(self, count=5):

        relationships = []

        agents_by_id = {
            agent.id: agent
            for agent in self.agents
        }

        for (
            pair,
            strength
        ) in self.relations.items():

            if strength <= 0:
                continue

            a_id, b_id = pair

            a = agents_by_id.get(
                a_id
            )

            b = agents_by_id.get(
                b_id
            )

            if a and b:

                relationships.append(
                    (
                        strength,
                        a.name,
                        b.name
                    )
                )

        relationships.sort(
            reverse=True
        )

        return relationships[:count]

    def save(
        self,
        filename="society_save.json"
    ):

        data = {

            "day":
                self.day,

            "food_price":
                self.food_price,

            "economy_multiplier":
                self.economy_multiplier,

            "births":
                self.births,

            "deaths":
                self.deaths,

            "history":
                self.history,

            "event_log":
                self.event_log,

            "agents":
                []
        }

        for agent in self.agents:

            data["agents"].append({

                "id":
                    agent.id,

                "name":
                    agent.name,

                "age":
                    agent.age,

                "gender":
                    agent.gender,

                "job":
                    agent.job,

                "money":
                    agent.money,

                "food":
                    agent.food,

                "energy":
                    agent.energy,

                "hunger":
                    agent.hunger,

                "health":
                    agent.health,

                "social":
                    agent.social,

                "happiness":
                    agent.happiness,

                "personality":
                    agent.personality,

                "ambition":
                    agent.ambition,

                "sociability":
                    agent.sociability,

                "generosity":
                    agent.generosity,

                "aggression":
                    agent.aggression,

                "x":
                    agent.x,

                "y":
                    agent.y,

                "partner":
                    agent.partner.id
                    if agent.partner
                    else None,

                "children":
                    [
                        child.id
                        for child in agent.children
                    ],

                "parents":
                    [
                        parent.id
                        for parent in agent.parents
                    ],

                "alive":
                    agent.alive,

                "memory":
                    agent.memory,

                "last_action":
                    agent.last_action,

                "age_ticks":
                    agent.age_ticks
            })

        with open(
            filename,
            "w"
        ) as file:

            json.dump(
                data,
                file,
                indent=2
            )

    def print_dashboard(self):

        stats = self.statistics()

        if not stats:
            return

        print(
            "\033[2J\033[H"
        )

        print(
            "=" * 70
        )

        print(
            "                         AI SOCIETY"
        )

        print(
            "=" * 70
        )

        print(
            f"Day:              {stats['day']}"
        )

        print(
            f"Population:       {stats['population']}"
        )

        print(
            f"Average Age:      {stats['average_age']:.1f}"
        )

        print(
            f"Average Happiness:{stats['average_happiness']:.1f}"
        )

        print(
            f"Average Health:   {stats['average_health']:.1f}"
        )

        print(
            f"Average Money:    ${stats['average_money']:.2f}"
        )

        print(
            f"Food Price:       ${stats['food_price']:.2f}"
        )

        print(
            f"Births:           {stats['births']}"
        )

        print(
            f"Deaths:           {stats['deaths']}"
        )

        print(
            "-" * 70
        )

        print(
            "JOBS"
        )

        for job, count in sorted(
            stats["jobs"].items(),
            key=lambda item:
            -item[1]
        ):

            print(
                f"{job:<15} {count}"
            )

        print(
            "-" * 70
        )

        print(
            "RICHEST"
        )

        for agent in self.richest():

            print(
                f"{agent.name:<15} "
                f"${agent.money:>8.2f} "
                f"{agent.job}"
            )

        print(
            "-" * 70
        )

        print(
            "HAPPIEST"
        )

        for agent in self.happiest():

            print(
                f"{agent.name:<15} "
                f"{agent.happiness:>6.1f} "
                f"{agent.last_action}"
            )

        print(
            "-" * 70
        )

        print(
            "STRONGEST RELATIONSHIPS"
        )

        for (
            strength,
            a,
            b
        ) in self.strongest_relationships():

            print(
                f"{a} <-> {b} "
                f"{strength:.1f}"
            )

        print(
            "-" * 70
        )

        print(
            "RECENT EVENTS"
        )

        for event in self.event_log[-5:]:

            print(event)

        print(
            "=" * 70
        )

    def run(
        self,
        days=5000,
        delay=0.01,
        display_every=25
    ):

        for _ in range(days):

            self.daily_update()

            if (
                self.day
                %
                display_every
                == 0
            ):

                self.print_dashboard()

            if delay > 0:

                time.sleep(delay)


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
