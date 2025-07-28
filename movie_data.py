"""
Movie data for collection browsing
Contains popular movies, latest releases, and random selections
"""

POPULAR_MOVIES = [
    {
        "name": "Avatar: The Way of Water",
        "rating": "7.6/10",
        "description": "Jake Sully lives with his newfound family formed on the planet of Pandora. Once a familiar threat returns to finish what was previously started, Jake must work with Neytiri and the army of the Na'vi race to protect their planet."
    },
    {
        "name": "Top Gun: Maverick", 
        "rating": "8.3/10",
        "description": "After thirty years, Maverick is still pushing the envelope as a top naval aviator, but must confront ghosts of his past when he leads TOP GUN's elite graduates on a mission that demands the ultimate sacrifice from those chosen to fly it."
    },
    {
        "name": "Spider-Man: No Way Home",
        "rating": "8.2/10", 
        "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear, forcing Peter to discover what it truly means to be Spider-Man."
    },
    {
        "name": "The Batman",
        "rating": "7.8/10",
        "description": "When a sadistic serial killer begins murdering key political figures in Gotham, Batman is forced to investigate the city's hidden corruption and question his family's involvement."
    },
    {
        "name": "Black Panther: Wakanda Forever",
        "rating": "6.7/10",
        "description": "The people of Wakanda fight to protect their home from intervening world powers as they mourn the death of King T'Challa."
    },
    {
        "name": "Jurassic World Dominion",
        "rating": "5.6/10",
        "description": "Four years after the destruction of Isla Nublar, dinosaurs now live and hunt alongside humans all over the world. This fragile balance will reshape the future and determine, once and for all, whether human beings are to remain the apex predators on a planet they now share with history's most fearsome creatures."
    },
    {
        "name": "Doctor Strange in the Multiverse of Madness",
        "rating": "6.9/10",
        "description": "Doctor Strange teams up with a mysterious teenage girl from his dreams who can travel across multiverses, to battle multiple threats, including other-universe versions of himself, which threaten to wipe out millions across the multiverse."
    },
    {
        "name": "Thor: Love and Thunder",
        "rating": "6.2/10",
        "description": "Thor enlists the help of Valkyrie, Korg and ex-girlfriend Jane Foster to fight Gorr the God Butcher, who intends to make the gods extinct."
    },
    {
        "name": "Minions: The Rise of Gru",
        "rating": "6.5/10",
        "description": "The untold story of one twelve-year-old's dream to become the world's greatest supervillain, in the 1970s when superstars like The Bee Gees dominated the charts."
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
        "name": "Aquaman and the Lost Kingdom",
        "rating": "5.7/10",
        "description": "Black Manta seeks revenge on Aquaman for his father's death. Wielding the Black Trident's power, he becomes a formidable foe. To defend Atlantis, Aquaman forges an alliance with his imprisoned brother."
    },
    {
        "name": "Wonka",
        "rating": "7.1/10", 
        "description": "The story will focus specifically on a young Willy Wonka and how he met the Oompa-Loompas on one of his earliest adventures."
    },
    {
        "name": "The Hunger Games: The Ballad of Songbirds & Snakes",
        "rating": "6.7/10",
        "description": "64 years before he becomes the tyrannical president of Panem, Coriolanus Snow sees a chance for a change in fortunes when he mentors Lucy Gray Baird, the female tribute from District 12."
    },
    {
        "name": "Napoleon",
        "rating": "6.4/10",
        "description": "An epic that details the checkered rise and fall of French Emperor Napoleon Bonaparte and his relentless journey to power through the prism of his addictive, volatile relationship with his wife, Josephine."
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
        "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency."
    },
    {
        "name": "The Godfather",
        "rating": "9.2/10", 
        "description": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son."
    },
    {
        "name": "Pulp Fiction",
        "rating": "8.9/10",
        "description": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption."
    },
    {
        "name": "Inception",
        "rating": "8.8/10",
        "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."
    },
    {
        "name": "Forrest Gump",
        "rating": "8.8/10",
        "description": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate and other historical events unfold from the perspective of an Alabama man with an IQ of 75."
    },
    {
        "name": "The Matrix",
        "rating": "8.7/10",
        "description": "When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence."
    },
    {
        "name": "Goodfellas",
        "rating": "8.7/10",
        "description": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito."
    },
    {
        "name": "Interstellar",
        "rating": "8.6/10",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
    },
    {
        "name": "Parasite",
        "rating": "8.5/10",
        "description": "A poor family schemes to become employed by a wealthy family and infiltrate their household by posing as unrelated, highly qualified individuals."
    },
    {
        "name": "The Avengers",
        "rating": "8.0/10",
        "description": "Earth's mightiest heroes must come together and learn to fight as a team if they are going to stop the mischievous Loki and his alien army from enslaving humanity."
    }
]