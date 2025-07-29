"""
Movie data for collection browsing
Contains popular movies, latest releases, and random selections
"""

POPULAR_MOVIES = [
    {
        "name": "The Shawshank Redemption",
        "rating": "9.3/10",
        "description": "Two imprisoned men bond over years, finding solace and redemption."
    },
    {
        "name": "The Godfather",
        "rating": "9.2/10",
        "description": "The aging patriarch of an organized crime dynasty transfers control."
    },
    {
        "name": "The Dark Knight",
        "rating": "9.0/10",
        "description": "Batman faces the Joker in a battle for Gotham City's soul."
    },
    {
        "name": "Avatar: The Way of Water",
        "rating": "7.6/10",
        "description": "Jake Sully protects his family on Pandora from returning threats."
    },
    {
        "name": "Top Gun: Maverick",
        "rating": "8.3/10",
        "description": "Maverick trains TOP GUN graduates for a dangerous mission."
    },
    {
        "name": "Spider-Man: No Way Home",
        "rating": "8.2/10",
        "description": "Peter Parker faces villains from other dimensions."
    },
    {
        "name": "Pulp Fiction",
        "rating": "8.9/10",
        "description": "Interconnected stories of crime in Los Angeles."
    },
    {
        "name": "The Lord of the Rings",
        "rating": "8.8/10",
        "description": "Hobbits and allies battle to destroy the One Ring."
    },
    {
        "name": "Forrest Gump",
        "rating": "8.8/10",
        "description": "Simple man witnesses and influences historical events."
    },
    {
        "name": "Inception",
        "rating": "8.8/10",
        "description": "Thief enters dreams to plant an idea in someone's mind."
    },
    {
        "name": "Fight Club",
        "rating": "8.8/10",
        "description": "Insomniac creates underground fight club with mysterious friend."
    },
    {
        "name": "The Matrix",
        "rating": "8.7/10",
        "description": "Hacker discovers reality is a computer simulation."
    },
    {
        "name": "Goodfellas",
        "rating": "8.7/10",
        "description": "Rise and fall of mob associate Henry Hill."
    },
    {
        "name": "Interstellar",
        "rating": "8.6/10",
        "description": "Farmer leads mission through wormhole to save humanity."
    },
    {
        "name": "The Silence of the Lambs",
        "rating": "8.6/10",
        "description": "FBI trainee seeks help from imprisoned cannibal."
    },
    {
        "name": "Dune",
        "rating": "8.0/10",
        "description": "A noble family becomes embroiled in a war for control over the galaxy's most valuable asset while its heir becomes troubled by visions of a dark future."
    },
    {
        "name": "No Time to Die",
        "rating": "7.3/10",
        "description": "James Bond has left active service. His peace is short-lived when Felix Leiter, an old friend from the CIA, turns up asking for help, leading Bond onto the trail of a mysterious villain armed with dangerous new technology."
    },
    {
        "name": "Fast X",
        "rating": "5.8/10",
        "description": "Dom Toretto and his family are targeted by the vengeful son of drug kingpin Hernan Reyes."
    },
    {
        "name": "Oppenheimer",
        "rating": "8.3/10",
        "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb."
    },
    {
        "name": "Barbie",
        "rating": "6.9/10",
        "description": "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land. However, when they get a chance to go to the real world, they soon discover the joys and perils of living among humans."
    },
    {
        "name": "Guardians of the Galaxy Vol. 3",
        "rating": "7.9/10",
        "description": "Still reeling from the loss of Gamora, Peter Quill must rally his team to defend the universe and protect one of their own."
    }
]

LATEST_MOVIES = [
    {
        "name": "Deadpool & Wolverine",
        "rating": "8.0/10",
        "description": "Wade Wilson teams up with Wolverine in multiverse adventure."
    },
    {
        "name": "Inside Out 2",
        "rating": "7.7/10",
        "description": "Riley's emotions navigate teenage challenges and new feelings."
    },
    {
        "name": "Bad Boys: Ride or Die",
        "rating": "6.8/10",
        "description": "Miami cops Marcus and Mike face their biggest threat yet."
    },
    {
        "name": "Dune: Part Two",
        "rating": "8.5/10",
        "description": "Paul Atreides leads rebellion against those who destroyed his family."
    },
    {
        "name": "Wonka",
        "rating": "7.1/10",
        "description": "Young Willy Wonka's early chocolate-making adventures."
    },
    {
        "name": "Scream VI",
        "rating": "6.5/10",
        "description": "Ghostface stalks survivors in New York City."
    },
    {
        "name": "John Wick: Chapter 4",
        "rating": "7.8/10",
        "description": "John Wick fights for freedom from High Table."
    },
    {
        "name": "Guardians of the Galaxy Vol. 3",
        "rating": "7.9/10",
        "description": "Peter Quill's team defends universe and protects their own."
    },
    {
        "name": "Fast X",
        "rating": "5.8/10",
        "description": "Dom's family faces their most lethal opponent ever."
    },
    {
        "name": "Indiana Jones 5",
        "rating": "6.7/10",
        "description": "Aging archaeologist faces final adventure."
    },
    {
        "name": "Napoleon",
        "rating": "6.4/10",
        "description": "Epic about French Emperor's rise and fall through relationship."
    },
    {
        "name": "Indiana Jones and the Dial of Destiny",
        "rating": "6.5/10",
        "description": "Archaeologist Indiana Jones races against time to retrieve a legendary artifact that can change the course of history."
    },
    {
        "name": "John Wick: Chapter 4",
        "rating": "7.7/10",
        "description": "John Wick uncovers a path to defeating The High Table. But before he can earn his freedom, Wick must face off against a new enemy with powerful alliances across the globe and forces that turn old friends into foes."
    },
    {
        "name": "Scream VI",
        "rating": "6.5/10",
        "description": "Following the latest Ghostface killings, the four survivors leave Woodsboro behind and start a fresh chapter."
    },
    {
        "name": "Ant-Man and the Wasp: Quantumania",
        "rating": "6.1/10",
        "description": "Scott Lang and Hope Van Dyne are dragged into the Quantum Realm, along with Hope's parents and Scott's daughter Cassie. Together they must find a way to escape, but what secrets is Hope's mother hiding, and who is the mysterious Kang?"
    }
]

RANDOM_MOVIES = [
    {
        "name": "The Shawshank Redemption",
        "rating": "9.3/10",
        "description": "Two imprisoned men bond over years, finding solace and redemption."
    },
    {
        "name": "Casablanca",
        "rating": "8.5/10",
        "description": "Nightclub owner helps ex-lover and husband escape Nazis."
    },
    {
        "name": "Toy Story",
        "rating": "8.3/10",
        "description": "Toys come to life when humans aren't around."
    },
    {
        "name": "Titanic",
        "rating": "7.9/10",
        "description": "Romance blooms aboard the doomed ocean liner."
    },
    {
        "name": "The Lion King",
        "rating": "8.5/10",
        "description": "Young lion prince flees his kingdom after father's death."
    },
    {
        "name": "Jurassic Park",
        "rating": "8.1/10",
        "description": "Dinosaurs are brought back to life in modern theme park."
    },
    {
        "name": "Star Wars",
        "rating": "8.6/10",
        "description": "Young farm boy joins rebellion against evil Empire."
    },
    {
        "name": "E.T.",
        "rating": "7.9/10",
        "description": "Boy befriends stranded alien trying to return home."
    },
    {
        "name": "Back to the Future",
        "rating": "8.5/10",
        "description": "Teen travels back in time and changes his parents' past."
    },
    {
        "name": "The Terminator",
        "rating": "8.0/10",
        "description": "Robot assassin sent back to kill future resistance leader."
    }
]