"""Case files: real, publicly reported product decisions that went wrong (or right), with the leadership lesson.

Facts were checked against public reporting (see `sources`) in Nov 2026. Keep claims modest: where reports disagree
(numbers, motives), say "about", "reported" or leave the detail out. tone: exemplary | cautionary | mixed.
"role" is the product-leadership area the case teaches (shown as a tag).
"""

CASES = [
    {
        "id": "sonos", "company": "Sonos", "year": "2024", "role": "Launch", "tone": "cautionary",
        "title": "The app that replaced the app",
        "summary": "Sonos shipped a rebuilt app to every customer at once, with familiar features missing. The fallout cost revenue, delayed new products and preceded the CEO's departure.",
        "story": [
            "In May 2024 Sonos replaced its mobile app with a rebuilt version for all users. Customers immediately reported missing features (such as sleep timers and parts of local music library support), accessibility gaps and reliability problems, and the old app could not simply be reinstalled. Reporting later said employees had raised concerns before launch.",
            "CEO Patrick Spence apologised publicly, the company said fixing the app would cost $20-30 million and delayed new hardware launches while it repaired the software. The Wall Street Journal reported the company put the revenue cost at at least $100 million. In January 2025 Spence stepped down and board member Tom Conrad became interim CEO.",
        ],
        "lesson": "Never force a big-bang replacement of a core experience without feature parity, accessibility, a staged rollout and a way back. Warnings from the team are evidence.",
        "sources": [("MacRumors: Sonos CEO steps down following disastrous app redesign (Jan 2025)", "https://www.macrumors.com/2025/01/13/sonos-ceo-steps-down-after-app-redesign/"),
                    ("MacRumors: Sonos execs launched ill-received app despite employee protests (Sep 2024)", "https://www.macrumors.com/2024/09/23/sonos-app-development-insight/")],
    },
    {
        "id": "unity", "company": "Unity", "year": "2023-24", "role": "Pricing", "tone": "cautionary",
        "title": "The per-install fee",
        "summary": "Unity announced a fee per game install that would also hit games already shipped. Developer backlash forced a retreat, and a year later the fee was cancelled before it was ever charged.",
        "story": [
            "In September 2023 Unity announced a Runtime Fee: once a game passed revenue and install thresholds, developers would pay up to $0.20 per install, including for games built and released under earlier terms. Developers protested that it was unpredictable, retroactive and exposed them to abuse such as repeated installs; some said they would switch engines.",
            "Within weeks Unity revised the plan (limiting it to higher subscription tiers and exempting existing games), and its CEO stepped down soon after. In September 2024 new CEO Matt Bromberg cancelled the Runtime Fee for games entirely, returning to seat-based subscriptions with price increases, and acknowledged the change should not have been introduced the way it was.",
        ],
        "lesson": "Platform pricing changes must be predictable, forward-looking and researched with customers. Exploiting switching costs burns trust you spent years building.",
        "sources": [("Unity: Unity is canceling the Runtime Fee (Sep 2024)", "https://unity.com/blog/unity-is-canceling-the-runtime-fee")],
    },
    {
        "id": "qwikster", "company": "Netflix", "year": "2011", "role": "Decision making", "tone": "cautionary",
        "title": "Qwikster",
        "summary": "Netflix raised prices by splitting DVD and streaming plans, then announced a separate DVD brand. Customers revolted; the split was reversed within weeks.",
        "story": [
            "In July 2011 Netflix separated its DVD-by-mail and streaming plans, raising the price for customers who wanted both by about 60%. In September CEO Reed Hastings published a post beginning 'I messed up', apologising for how the change was communicated, and announcing that the DVD business would become a separate service called Qwikster, with its own website and account.",
            "The reaction was overwhelmingly negative. In October 2011 Netflix abandoned Qwikster while keeping the separate pricing. The company reported losing hundreds of thousands of US subscribers that quarter and its share price fell sharply, though the strategic bet on streaming went on to define the company.",
        ],
        "lesson": "A right long-term direction can still be executed badly. Separate the strategic decision from how it lands on customers, and test the customer experience of the change before committing.",
        "sources": [("Digital Trends: Netflix CEO explains price hike, renames DVD service Qwikster (2011)", "https://www.digitaltrends.com/mobile/netflix-ceo-explains-price-hike-renames-dvd-service-qwikster-adds-video-games/")],
    },
    {
        "id": "firephone", "company": "Amazon", "year": "2014", "role": "Strategy", "tone": "cautionary",
        "title": "The Fire Phone",
        "summary": "Amazon's smartphone launched with 3D effects and a premium, carrier-exclusive price. Within months it was nearly free, and Amazon took a $170 million charge.",
        "story": [
            "Amazon launched the Fire Phone in mid-2014, exclusive to AT&T in the US, priced like a premium phone, with 'Dynamic Perspective' 3D effects and Firefly, a feature that recognised products and media to buy. Reviews questioned what problem the phone solved for buyers compared with established phones.",
            "Weeks later the price was cut to 99 cents on a two-year contract. In October 2014 Amazon disclosed a charge of about $170 million, mostly for unsold Fire Phone inventory and supplier commitments. Amazon later said the lessons fed into later devices such as Echo.",
        ],
        "lesson": "Novel features that impress the builders are not a reason to switch. Start from the customer's job and the alternatives they already use, and size bets so failure is survivable.",
        "sources": [("Fierce Network: Amazon takes $170M writedown on Fire Phone (2014)", "https://www.fierce-network.com/wireless/amazon-takes-170m-writedown-fire-phone")],
    },
    {
        "id": "googleplus", "company": "Google", "year": "2011-19", "role": "Strategy", "tone": "cautionary",
        "title": "Google+",
        "summary": "Google launched a social network to answer Facebook and pushed it through its other products. Seven years later Google said usage was minimal and shut the consumer version down.",
        "story": [
            "Google+ launched in 2011 as Google's answer to Facebook, and Google integrated it widely across its products, including requiring Google+ profiles for some features. Sign-up numbers grew, but sustained engagement did not follow.",
            "In October 2018 Google's 'Project Strobe' post announced the end of consumer Google+, saying it had not achieved broad consumer or developer adoption and that most user sessions were very short. The announcement came alongside the disclosure of a bug in a Google+ API that could expose profile data. The consumer service closed in April 2019.",
        ],
        "lesson": "A strategy defined by a competitor, plus distribution forced through other products, does not create a reason to use something. Measure engagement and retention, not accounts created.",
        "sources": [("Google: Project Strobe, protecting your data and sunsetting consumer Google+ (2018)", "https://blog.google/technology/safety-security/project-strobe/")],
    },
    {
        "id": "quibi", "company": "Quibi", "year": "2020", "role": "Discovery", "tone": "cautionary",
        "title": "$1.75 billion, six months",
        "summary": "Quibi raised $1.75 billion for premium short shows made only for phones and shut down about six months after launch.",
        "story": [
            "Quibi, founded by Jeffrey Katzenberg and Meg Whitman, raised about $1.75 billion before launching in April 2020 with high-budget shows in episodes under ten minutes, designed for watching on the go on phones. At launch users could not easily share clips or watch on their TVs, and the pandemic had just removed most commuting.",
            "In October 2020 the founders announced the company would wind down, writing that it had failed either because the idea itself wasn't strong enough to justify a standalone streaming service or because of its timing.",
        ],
        "lesson": "Money and talent don't replace evidence that customers want the thing. Test the core assumptions (the job, the context, the willingness to pay) before betting the company.",
        "sources": [("CBS News: Quibi shutting down (2020)", "https://www.cbsnews.com/news/quibi-shutting-down/")],
    },
    {
        "id": "windows8", "company": "Microsoft", "year": "2012", "role": "Discovery", "tone": "cautionary",
        "title": "Where did the Start menu go?",
        "summary": "Windows 8 replaced the Start menu with a touch-first Start screen for every PC. Desktop users struggled, and Microsoft restored familiar elements in later versions.",
        "story": [
            "Windows 8 (2012) introduced a full-screen, tile-based Start screen designed for touch devices and removed the traditional Start button and menu, for keyboard-and-mouse desktop users as well as tablets.",
            "Many desktop users found it confusing. Windows 8.1 (2013) brought back a Start button and an option to boot to the desktop, and Windows 10 (2015) restored a Start menu combining the old menu with tiles.",
        ],
        "lesson": "Designing for the future segment shouldn't break the current one. Segment users by context and test with real desktop users before removing what they rely on.",
        "sources": [("Wikipedia: Windows 8 (reception and changes in 8.1)", "https://en.wikipedia.org/wiki/Windows_8")],
    },
    {
        "id": "tropicana", "company": "Tropicana (PepsiCo)", "year": "2009", "role": "Launch", "tone": "cautionary",
        "title": "The carton nobody recognised",
        "summary": "A redesigned orange juice carton dropped the brand's familiar orange-and-straw image. Sales fell sharply and the old design came back within about two months.",
        "story": [
            "In January 2009 Tropicana launched new packaging for Pure Premium, replacing the familiar orange pierced by a straw with a glass of juice and a minimalist look. Shoppers complained that it looked generic and was hard to find on shelves.",
            "Reported retail data showed unit sales fell about 20% between early January and late February. On 23 February 2009 the company said it would bring back the old design, acknowledging it had underestimated customers' emotional bond with the packaging.",
        ],
        "lesson": "Familiar cues are part of the product. Test redesigns with real behaviour (finding and buying), not only opinions about attractiveness, and launch big changes in stages.",
        "sources": [("The Branding Journal: What to learn from Tropicana's packaging redesign failure", "https://www.thebrandingjournal.com/2015/05/what-to-learn-from-tropicanas-packaging-redesign-failure/")],
    },
    {
        "id": "newcoke", "company": "Coca-Cola", "year": "1985", "role": "Research", "tone": "cautionary",
        "title": "New Coke",
        "summary": "Taste tests said people preferred a sweeter formula. Coca-Cola replaced its original, and brought it back 79 days later after a public outcry.",
        "story": [
            "In April 1985 Coca-Cola replaced its formula with a sweeter one after extensive blind taste tests suggested people preferred it to both old Coke and Pepsi. The research measured taste in a sip; it didn't measure what the brand meant to people.",
            "The backlash was intense: letters, calls and protests from customers who felt something of theirs had been taken. In July 1985, 79 days later, the company brought back the original as Coca-Cola Classic.",
        ],
        "lesson": "Research answers the question it asks. Measure attachment, habit and identity, not just the attribute you're changing, and give people a choice when replacing something loved.",
        "sources": [("The Coca-Cola Company: New Coke, the most memorable marketing blunder ever?", "https://www.coca-colacompany.com/about-us/history/new-coke-the-most-memorable-marketing-blunder-ever")],
    },
    {
        "id": "slack", "company": "Slack (Tiny Speck)", "year": "2013-14", "role": "Positioning", "tone": "exemplary",
        "title": "From a failed game to a new category",
        "summary": "A game studio's internal chat tool became Slack. Its founder's memo on selling the outcome, not the features, is a classic of positioning.",
        "story": [
            "Tiny Speck built an online game, Glitch, which shut down in 2012. The team had built an internal messaging tool along the way; it became Slack, released in preview in 2013 and launched in 2014, and grew quickly through teams inviting colleagues.",
            "In July 2014 Stewart Butterfield wrote a memo to the team, 'We Don't Sell Saddles Here': sell horse riding, not saddles. Customers weren't buying 'group chat'; they were buying a less busy, more productive working life for their team, and every part of the product and marketing should serve that.",
        ],
        "lesson": "Follow the evidence when it points to a different product, and position around the outcome customers buy, not the category of the thing.",
        "sources": [("Stewart Butterfield: We Don't Sell Saddles Here (2014)", "https://medium.com/@stewart/we-dont-sell-saddles-here-4c59524d650d")],
    },
    {
        "id": "superhuman", "company": "Superhuman", "year": "2017-18", "role": "Product-market fit", "tone": "exemplary",
        "title": "An engine for product-market fit",
        "summary": "Superhuman measured product-market fit with one survey question, segmented the answers, and split its roadmap to raise the score.",
        "story": [
            "Before broad launch, Rahul Vohra's team asked users Sean Ellis's question: how would you feel if you could no longer use Superhuman? About a fifth answered 'very disappointed', well below the 40% benchmark.",
            "They segmented the very disappointed group to define their high-expectation customer, learned what those users loved (speed above all), and asked what held back the somewhat disappointed who shared that benefit. They spent roughly half the roadmap on each. Vohra reported the score rising well above 40% within about a year.",
        ],
        "lesson": "Product-market fit can be measured, segmented and improved deliberately, by focusing on who loves you and what blocks the people closest to loving you.",
        "sources": [("Rahul Vohra: How Superhuman built an engine to find product-market fit", "https://blog.superhuman.com/how-superhuman-built-an-engine-to-find-product-market-fit/")],
    },
    {
        "id": "bing", "company": "Microsoft Bing", "year": "2012", "role": "Experimentation", "tone": "exemplary",
        "title": "The idea that waited six months",
        "summary": "A low-priority idea to change how ad headlines were displayed sat in the backlog for months. When finally tested, it raised revenue about 12%.",
        "story": [
            "Ron Kohavi and Stefan Thomke describe a Bing employee's suggestion to lengthen ad title lines by combining them with text from the line below. It was judged low priority and waited more than six months, until an engineer tested it cheaply.",
            "The experiment showed a revenue increase of about 12%, worth over $100 million a year in the US at the time, without hurting user experience metrics. It was one of the most valuable ideas in Bing's history, and nobody had predicted it.",
        ],
        "lesson": "Intuition is a poor predictor of what works. Cheap, trustworthy experimentation lets small ideas prove their value and stops big ideas from shipping on opinion.",
        "sources": [("Kohavi and Thomke: The Surprising Power of Online Experiments (HBR, 2017)", "https://hbr.org/2017/09/the-surprising-power-of-online-experiments")],
    },
    {
        "id": "booking", "company": "Booking.com", "year": "2020", "role": "Experimentation", "tone": "exemplary",
        "title": "A culture of experimentation",
        "summary": "Booking.com runs huge numbers of controlled experiments and lets employees test ideas without management approval, with strict standards.",
        "story": [
            "Stefan Thomke's HBR article describes Booking.com running more than 1,000 experiments at any given time, and tens of thousands a year, on a shared platform. Employees can launch tests without asking permission from management, but experiments follow common standards and are visible to everyone.",
            "Leaders' role shifts from deciding by opinion to setting the system: goals, guardrails, ethics and the infrastructure that makes trustworthy tests cheap. Most experiments fail, and that is expected.",
        ],
        "lesson": "Experimentation at scale is a leadership and culture choice: democratise testing, keep the standards high, and accept that most ideas don't work.",
        "sources": [("Stefan Thomke: Building a Culture of Experimentation (HBR, 2020)", "https://hbr.org/2020/03/building-a-culture-of-experimentation")],
    },
    {
        "id": "threads", "company": "Meta (Threads)", "year": "2023-24", "role": "Growth", "tone": "mixed",
        "title": "100 million sign-ups in days",
        "summary": "Threads used Instagram accounts to reach 100 million sign-ups in about five days. Engagement fell sharply soon after; Meta then rebuilt habits feature by feature.",
        "story": [
            "Meta launched Threads in July 2023. Because people could sign up with their Instagram account and follow the same people in one tap, it passed 100 million sign-ups in about five days, a record for an app.",
            "Reported usage then dropped steeply over the following weeks as many users found little reason to return. Meta added missing features (a web version, search, a following feed) and later reported Threads growing to hundreds of millions of monthly users.",
        ],
        "lesson": "Borrowed distribution solves the cold start, not retention. Sign-ups measure reach; a lasting habit needs a core use that brings people back.",
        "sources": [("Wikipedia: Threads (social network)", "https://en.wikipedia.org/wiki/Threads_(social_network)")],
    },
    {
        "id": "adobecc", "company": "Adobe", "year": "2013", "role": "Business model", "tone": "exemplary",
        "title": "From boxes to subscriptions",
        "summary": "Adobe stopped selling Creative Suite licences and moved everyone to Creative Cloud subscriptions, accepting a backlash and a temporary revenue dip.",
        "story": [
            "In May 2013 Adobe announced it would stop developing new versions of the boxed Creative Suite and focus on Creative Cloud, a subscription. Many users protested, including a widely signed petition, and revenue dipped during the transition as large upfront licence sales were replaced by monthly payments.",
            "Adobe prepared investors with new metrics such as recurring revenue and subscriber numbers, and subscription revenue grew to become the large majority of the business, with more frequent updates for customers.",
        ],
        "lesson": "A business model change can be the most important product decision. Explain the customer benefit, give investors the right metrics for the transition, and expect a dip before the gain.",
        "sources": [("Wikipedia: Adobe Creative Cloud (history)", "https://en.wikipedia.org/wiki/Adobe_Creative_Cloud")],
    },
    {
        "id": "basecamp", "company": "Basecamp", "year": "2019", "role": "Operating cadence", "tone": "exemplary",
        "title": "Shape Up",
        "summary": "Basecamp published its own way of building product: six-week cycles, fixed time and variable scope, and work shaped by senior people before a team commits.",
        "story": [
            "Ryan Singer's free book Shape Up (2019) describes how Basecamp works: senior people 'shape' a problem to an appetite (how much time it is worth) instead of estimating a solution; a betting table chooses which shaped pitches get the next six-week cycle; small teams have full responsibility within the cycle; two-week cool-downs follow.",
            "A 'circuit breaker' means projects that don't finish within their cycle don't get extended by default, which limits runaway projects. There are no backlogs carried forward; good ideas come back.",
        ],
        "lesson": "Process is a design choice. Fixed time with variable scope, appetite instead of estimates, and explicit bets can replace much of the ceremony teams inherit.",
        "sources": [("Basecamp: Shape Up (Ryan Singer, 2019)", "https://basecamp.com/shapeup")],
    },
    {
        "id": "spotify", "company": "Spotify", "year": "2012-20", "role": "Org design", "tone": "mixed",
        "title": "The 'Spotify model'",
        "summary": "A 2012 paper about squads, tribes, chapters and guilds was copied by companies worldwide. Former insiders later said Spotify itself never fully worked that way.",
        "story": [
            "In 2012 Henrik Kniberg and Anders Ivarsson described how Spotify organised engineering: autonomous squads grouped into tribes, with chapters and guilds for craft and knowledge sharing. The paper spread widely and many companies adopted 'the Spotify model' wholesale.",
            "In 2020 former Spotify product manager Jeremiah Lee wrote that the model was an aspiration rather than how Spotify consistently operated, and that it caused problems such as unclear accountability in its matrix structure. The authors themselves had warned against copying it.",
        ],
        "lesson": "Copy principles, not org charts. Design your structure for your strategy and architecture, and judge it by outcomes and accountability.",
        "sources": [("Jeremiah Lee: Spotify's Failed #SquadGoals (2020)", "https://www.jeremiahlee.com/posts/failed-squad-goals/")],
    },
    {
        "id": "airbnb", "company": "Airbnb", "year": "2023-24", "role": "Org design", "tone": "mixed",
        "title": "Founder mode",
        "summary": "Airbnb's CEO described redesigning how the company builds product, with more central control and fewer projects. His talk inspired the 'Founder Mode' debate.",
        "story": [
            "Brian Chesky has described in interviews and talks how, after the pandemic, Airbnb reorganised to a more functional structure, cut the number of simultaneous projects, reviewed work in much more detail himself, and changed the role of product management, combining much of it with product marketing.",
            "Paul Graham's 2024 essay 'Founder Mode', inspired by a Chesky talk at Y Combinator, argued founders should stay close to the details rather than delegate everything to managers. The essay was widely shared and widely criticised for being vague and excusing micromanagement.",
        ],
        "lesson": "Leaders' involvement is a design choice, not a personality trait. Decide explicitly where the CEO goes deep, what teams own, and how product management's role fits the company.",
        "sources": [("Paul Graham: Founder Mode (2024)", "https://paulgraham.com/foundermode.html")],
    },
    {
        "id": "fbfeed", "company": "Facebook", "year": "2006", "role": "Change & trust", "tone": "mixed",
        "title": "Calm down. Breathe. We hear you.",
        "summary": "Facebook's News Feed launched to protests over privacy. Within days the company added controls; the feed became the core of the product.",
        "story": [
            "In September 2006 Facebook launched News Feed, showing users a stream of their friends' activity. Information that had been visible on profiles was now pushed to everyone, and many users felt exposed; protest groups against the feature attracted large numbers of members.",
            "Mark Zuckerberg posted a response beginning 'Calm down. Breathe. We hear you.', and within days Facebook introduced privacy controls over what appeared in the feed. Usage grew and the feed became central to Facebook and to social products generally.",
        ],
        "lesson": "A change can be right and still violate expectations of privacy. Anticipate how visibility changes feel, give control at launch, and respond quickly when trust is shaken.",
        "sources": [("Wikipedia: Feed (Facebook)", "https://en.wikipedia.org/wiki/Feed_(Facebook)")],
    },
    {
        "id": "klarna", "company": "Klarna", "year": "2024-25", "role": "AI products", "tone": "mixed",
        "title": "Two-thirds of support chats, then a step back",
        "summary": "Klarna's AI assistant handled two-thirds of customer-service chats in its first month. A year later the CEO said cost focus had hurt quality and brought humans back into reach.",
        "story": [
            "In February 2024 Klarna announced its AI assistant had handled 2.3 million conversations in its first month, two-thirds of its customer-service chats, doing work it equated to 700 full-time agents, resolving issues in under two minutes instead of eleven, with a 25% drop in repeat inquiries.",
            "In 2025 CEO Sebastian Siemiatkowski said the focus on cost had led to lower quality in places and the company would make sure customers could always reach a human, recruiting people for customer service again.",
        ],
        "lesson": "Automation rates and cost savings are not the whole story. Measure resolution quality and customer outcomes, and keep a good path to humans.",
        "sources": [("Klarna: AI assistant handles two-thirds of customer service chats in its first month (2024)", "https://www.klarna.com/international/press/klarna-ai-assistant-handles-two-thirds-of-customer-service-chats-in-its-first-month/")],
    },
    {
        "id": "crowdstrike", "company": "CrowdStrike", "year": "2024", "role": "Reliability", "tone": "cautionary",
        "title": "One update, 8.5 million machines",
        "summary": "A faulty content update to a security product crashed about 8.5 million Windows devices worldwide, grounding flights and disrupting hospitals and banks.",
        "story": [
            "On 19 July 2024 CrowdStrike pushed a configuration update to its Falcon sensor that caused Windows machines to crash. Microsoft estimated about 8.5 million devices were affected, under 1% of Windows machines, but they included critical systems at airlines, hospitals, banks and broadcasters.",
            "Because the update went to all customers at once and affected machines often needed manual recovery, restoring service took days for many organisations. CrowdStrike committed to staged deployment of such content updates and more testing.",
        ],
        "lesson": "Blast radius is a product decision. Staged rollouts, canaries and fast rollback paths matter most for software that runs everywhere and at a deep level.",
        "sources": [("Microsoft: Helping our customers through the CrowdStrike outage (2024)", "https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/")],
    },
    {
        "id": "southwest", "company": "Southwest Airlines", "year": "2022", "role": "Technical debt", "tone": "cautionary",
        "title": "The holiday meltdown",
        "summary": "Winter storms tipped Southwest's operations into collapse when its crew scheduling couldn't recover. The US government imposed a record $140 million penalty.",
        "story": [
            "In late December 2022, after severe winter storms, Southwest's network collapsed: its systems and processes for reassigning crews could not keep up, and the airline cancelled about 16,900 flights over the holiday period, stranding around two million passengers. Southwest's crew scheduling technology was widely reported as a central weakness.",
            "In December 2023 the US Department of Transportation announced a $140 million civil penalty, 30 times larger than any previous penalty for consumer protection violations, on top of more than $600 million in refunds and reimbursements Southwest had paid.",
        ],
        "lesson": "Underinvestment in core systems is a business risk that compounds silently until a stress event. Treat critical technical health as a funded, owned product priority.",
        "sources": [("US Department of Transportation: Southwest Airlines penalised $140 million for 2022 holiday meltdown", "https://www.transportation.gov/briefing-room/dot-penalizes-southwest-airlines-140-million-2022-holiday-meltdown")],
    },
]

CASE_BY_ID = {c["id"]: c for c in CASES}
