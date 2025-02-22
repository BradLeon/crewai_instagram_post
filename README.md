# {{crew_name}} Crew

Welcome to the instagram_post_flow Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <=3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```

### Customizing

**Add your `OPENROUTER_API_KEY` into the `.env` file**
In these demo project, we use OpenRouter API to access DeepSeek and Gemini model, DeepSeek to cover txt2txt, Gemini to process image2txt. We also use a Stable Diffusion as a Local Server to generate images.


- Modify `src/instagram_post_flow/config/agents.yaml` to define your agents
- Modify `src/instagram_post_flow/config/tasks.yaml` to define your tasks
- Modify `src/instagram_post_flow/crew.py` to add your own logic, tools and specific args
- Modify `src/instagram_post_flow/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
crewai flow kickoff
```

This command initializes the instagram_post_flow Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The instagram_post_flow Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

##  Project Result
    We use the following inputs as a demo to generate the instagram post:
    inputs =  {
        "product_website": "https://www.kickstarter.com/projects/yoshiakiito/new-morphits-transforming-wooden-toy-snake-and-turtle-combo?ref=discovery_category&total_hits=1504&category_id=396",
        "product_details": "Morphits® emerged from a vision to blend the classic charm of wooden toys with contemporary innovation. Crafted by the acclaimed artist and designer Yoshiaki Ito, Morphits® has captured hearts worldwide with its marriage of traditional craftsmanship and modern aesthetics. Each Morphits® piece is meticulously handcrafted from sustainable wood, ensuring both durability and timeless beauty."
        }
    

    outputs = {
        Post1 : {
            title: ✨ **Rediscover Play with Morphits®** ✨
            description: Transform playtime with our handcrafted Snake & Turtle Combo! 🐍🐢 Designed by master artist Yoshiaki Ito, these sustainable wooden toys spark creativity and imagination. Perfect for eco-conscious families who value timeless craftsmanship. 🌿
            👉 **Join the movement! Back Morphits® on Kickstarter today and bring innovation to your home.**
            #MorphitsToys #SustainablePlay #YoshiakiIto #WoodenToys #CreativePlay
            image: api_out/txt2img/txt2img-20250221-181147-0.png
        }
        Post2: {
            title: 🌟 **Where Tradition Meets Innovation** 🌟  
            description: Meet Morphits®: the wooden toy that transforms play! 🐍➡️🐢 Handcrafted from sustainable wood, each piece is a work of art by Yoshiaki Ito. Encourage endless creativity and eco-friendly fun for your little ones. 🌍  🚀 **Don’t miss out! Support Morphits® on Kickstarter and redefine playtime.**  #MorphitsToys #SustainablePlay #YoshiakiIto #WoodenToys #CreativePlay  
            image: api_out/txt2img/txt2img-20250221-181243-0.png
        }
        Post3: {
            title: 🎨 **Art Meets Play with Morphits®** 🎨 
            description: Discover the magic of Morphits®—a transforming Snake & Turtle Combo that blends timeless craftsmanship with modern innovation. 🌳 Designed by Yoshiaki Ito, these sustainable wooden toys inspire creativity and endless possibilities. 💡 **Be part of the journey! Back Morphits® on Kickstarter and bring artful play to your home.#MorphitsToys #SustainablePlay #YoshiakiIto #WoodenToys #CreativePlay
            image: api_out/txt2img/txt2img-20250221-181214-0.png
        }

    }


## Support

For support, questions, or feedback regarding the instagram_post_flow Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
