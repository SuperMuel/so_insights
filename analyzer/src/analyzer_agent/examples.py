from shared.models import Article
from .types import Quote, Section
import json


EXAMPLE_SECTIONS = [
    Section(
        title="Expansion internationale et investissements dans l'alimentation pour animaux",
        description="Cette section explore les initiatives d'expansion internationale et les investissements majeurs dans le secteur pet-food, en soulignant comment les acteurs clés, tels que Normandise Pet Food et Nestlé/Purina, renforcent leur position sur le marché global. Le rapport passera en revue les stratégies d'acquisition de fonds et de partenariats internationaux qui soutiennent la croissance dans l'industrie de l'alimentation pour animaux de compagnie.",
        supporting_quotes=[
            Quote(
                text="« Cette opération marque une étape cruciale dans notre développement. Avec le soutien renouvelé de Bpifrance et Sofinormandie, nous sommes prêts à conquérir de nouveaux marchés et à renforcer notre position de leader en Europe. »",
                source=7,
                relevance_justification="Ce passage de Normandise Pet Food illustre l'ambition d'expansion internationale et l'importance des partenariats financiers dans le renforcement de la position mondiale, ce qui est essentiel pour la veille sur le marché pet-food.",
            ),
            Quote(
                text="« The first 12 months (or 24 months for larger puppy breeds) are a crucial developmental period for puppies and kittens, learning new skills and exploring the world around them. »",
                source=18,
                relevance_justification="Cette citation de l'article sur le recrutement chez Nestlé Purina PetCare met en avant l'attention portée au développement des animaux dans les stratégies de marque, soulignant l'investissement dans le capital d'image et le marché à long terme.",
            ),
        ],
    ),
    Section(
        title="Innovations et stratégies marketing dans le secteur pet-food",
        description="Cette section se concentre sur les innovations produits et les stratégies marketing adoptées par les acteurs du secteur de l'alimentation pour animaux. Elle met l'accent sur la création de concepts novateurs, l'évolution des modèles de distribution, et la manière dont les entreprises se différencient par leur approche centrée sur le client et la qualité des produits.",
        supporting_quotes=[
            Quote(
                text="« J’ai démarré dans un local à l’entrée de Villeneuve-sur-Lot. J’étais derrière le comptoir. Mais dès le départ, j’avais l’intention de multiplier l’enseigne Animal Factory, sans la franchiser. »",
                source=24,
                relevance_justification="Cette citation de l'article sur Animal Factory illustre le caractère précurseur et innovant du concept de distribution en pet-food, en mettant l'accent sur la différenciation par le modèle de vente.",
            ),
            Quote(
                text="« Je ne vends pas juste des produits, je m’intéresse à mes clients et à leurs animaux. »",
                source=25,
                relevance_justification="Cette remarque de Damien Laval montre l'importance d'une approche marketing centrée sur la relation client et la qualité du service dans le secteur pet-food, soulignant la stratégie de fidélisation.",
            ),
        ],
    ),
    Section(
        title="Influence des multinationales et enjeux de gouvernance dans l'alimentation pour animaux",
        description="Cette section analyse l'impact des grands groupes, notamment Nestlé/Purina et Mars Petcare, sur la dynamique du marché de l'alimentation pour chiens et chats. Elle examine les pratiques de lobbying, la gouvernance interne et les stratégies d'influence qui façonnent les tendances et les décisions réglementaires dans le secteur.",
        supporting_quotes=[
            Quote(
                text="« Les carnets de Nestlé : révélations sur le lobbying secret de la firme »",
                source=17,
                relevance_justification="Cette citation met en lumière les pratiques de lobbying et d'influence de Nestlé, illustrant comment les multinationales influent sur la gouvernance et la régulation du marché pet-food.",
            ),
            Quote(
                text="« ... et 28 milliards de dollars CA provenant de la nourriture pour animaux vendue par Nestlé/Purina, un des actionnaires d’IVC Evidensia. »",
                source=8,
                relevance_justification="Ce passage démontre l'ampleur économique de l'alimentation pour animaux dans les revenus des multinationales comme Nestlé/Purina, soulignant ainsi leur rôle dominant et les enjeux de gouvernance dans le secteur.",
            ),
        ],
    ),
]

EXAMPLE_ARTICLES_IDS = [
    "679a0ab01826e4e3526caf57",
    "679a0ab01826e4e3526caf5d",
    "679a0ab01826e4e3526caf5c",
    "679a0ab01826e4e3526caf63",
    "679a0ab01826e4e3526caf45",
    "679a0ab01826e4e3526caf64",
    "679a0ab01826e4e3526caf42",
    "679a0ab01826e4e3526caf56",
    "679a0ab01826e4e3526caf55",
    "679a0ab01826e4e3526caf69",
    "679a0ab01826e4e3526caf46",
    "679a0ab01826e4e3526caf6e",
    "679a0ab01826e4e3526caf4b",
    "679a0ab01826e4e3526caf47",
    "679a0ab01826e4e3526caf4c",
    "679a0ab01826e4e3526caf68",
    "679a0ab01826e4e3526caf4d",
    "679a0ab01826e4e3526caf65",
    "679a0ab01826e4e3526caf72",
    "679a0ab01826e4e3526caf6a",
    "679a0ab01826e4e3526caf74",
    "679a0ab01826e4e3526caf48",
    "679a0ab01826e4e3526caf6b",
    "679a0ab01826e4e3526caf6c",
    "679a0ab01826e4e3526caf44",
    "679a0ab01826e4e3526caf6d",
    "679a0ab01826e4e3526caf43",
    "679a0ab01826e4e3526caf5f"
]

