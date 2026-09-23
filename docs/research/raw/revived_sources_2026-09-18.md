# Г60 — Добор оживших источников (сырьё)

Дата: 2026-09-18. Файл пишется по ходу, после каждого вызова.

## Журнал

### 0. Постановка прочитана
- Промпт `docs/research/queue/prompts/g60_prompt.md` и раздел Г60 GAP_QUEUE (стр. 3554–3653) прочитаны.
- Поправки лидера: mkb.ru, colvir.ru, reg.ubrr.ru → Г58 (`bank_statement_corpus_pass6_2026-09-18.md`); sec.gov/Champion → Г59 (`legal_license_tail_2026-09-18.md`); fstec.ru → Г59. Не повторяю.
- Уже известно из Г59 (стр. 301–304 `legal_license_tail_2026-09-18.md`): Felfernig & Burke — страница ACM FREE ACCESS, но `fetch('/doi/pdf/…')` изнутри страницы → 403 text/html 5 942 б; researchr: «pages 3» → Г59 истолковал как одностраничный тезис туториала. 🔴 Это толкование требует проверки: у ACM ICEC '08 «Article No. 3» — номер статьи, а не число страниц. Проверяю первым.
- Fano & Kurth 2003 (IUI '03, doi 10.1145/604045.604057): реферат есть, PDF — Turnstile, CiteSeerX PDF → 500.

### 1. Felfernig & Burke ICEC '08 — попытки
- Браузер `new_page dl.acm.org/doi/10.1145/1409540.1409544` (18.09.2026, вкладка 40): **Cloudflare Turnstile** «Performing security verification … checkbox "Verify you are human"», Ray ID a3d086cbdcee783c. Утром та же страница открывалась с FREE ACCESS — значит сейчас наш выход в режиме проверки; капчу не прожимаю по правилу.
- 🔴 **Crossref API** `api.crossref.org/works/10.1145/1409540.1409544` → title «Constraint-based recommender systems», **page: "1-10"**, авторы A. Felfernig (University of Klagenfurt), R. Burke (DePaul University Chicago), тип proceedings-article, ссылка на PDF `dl.acm.org/doi/pdf/10.1145/1409540.1409544`.
  → **ОПРОВЕРЖЕНИЕ записи Г59:** «pages 3» у researchr — это номер статьи (Article No. 3), а НЕ объём. Статья — **10 страниц**, полноценный обзор, а не «одностраничный тезис туториала». Вывод Г59 «закрывать нечего — источник однострочный» неверен; полный текст всё ещё нужно добыть.
- Crossref `10.1145/604045.604057` → «Personal choice point», **pp. 46–52** (7 страниц), Fano & Kurth, Accenture Technology Labs, Chicago; IUI '03.

- Каналы PDF `dl.acm.org/doi/pdf/10.1145/1409540.1409544`: curl+UA **403** 5 750 б text/html · `curl -sk --http1.1` **403** 5 750 б · `r.jina.ai` 200 на 200 б, внутри «Target URL returned error 403… Enable JavaScript and cookies» (заглушка, не текст) · Exa fetch pdf и fullHtml → **CRAWL_LIVECRAWL_TIMEOUT** · браузер → Turnstile.
- Semantic Scholar API: CorpusId 2081947, citationCount **310**, openAccessPdf **CLOSED**; `pdfs.semanticscholar.org/cafa/…pdf` → 202 0 б (AWS WAF challenge). Fano & Kurth: CorpusId 2201049, 29 цитирований, CLOSED; Unpaywall `10.1145/604045.604057` → is_oa false, has_repository_copy false.
- Авторские страницы: `felfernig.sai.tugraz.at/publications/` 200 28 005 б (ICEC '08 в списке без PDF — проверено Г18.2, стр. 1657 `closed_forever_retry_2026-09-16.md`: «у авторской группы нет собственной копии» для IUI '08); Burke DePaul `facweb.cdm.depaul.edu/rburke/pubs/` 404, `josquin.cti.depaul.edu/~rburke` 000.
- Exa search (2 запроса): страница ACM (через зеркало psycnet.apa.org) даёт **дословно** «Article No.: 3, Pages 1 - 10 … Published: 19 August 2008 … 177 citation, 3,101 Downloads» и реферат (полный, длиннее, чем в Г59):
  > «Recommender systems support users in identifying products and services in e-commerce and other information-rich environments. Recommendation problems have a long history as a successful AI application area, with substantial interest beginning in the mid-1990s, and increasing with the subsequent rise of e-commerce. Recommender systems research long focused on recommending only simple products such as movies or books; constraint-based recommendation now receives increasing attention due to the capability of recommending complex products and services. In this paper, we first introduce a taxonomy of recommendation knowledge sources and algorithmic approaches. We then go on to discuss the most prevalent techniques of constraint-based recommendation and outline open research issues.»
  Из списка литературы статьи (та же страница): «Felfernig, A., Isak, K., Szabo, K., and Zachar, P. 2007. The VITA Financial Services Sales Support Environment, AAAI/IAAI 2007, pp. 1692–1699»; «Felfernig, A., Friedrich, G., Teppan, E., and Isak, K 2008. Intelligent Debugging and Repair of Utility Constraint Sets…, IUI».
  Вторичные источники подтверждают объём: Lubos et al. RecSys 2023 и SPLC 2023 — «Article 3, 10 pages»; WeeVis (arXiv 2102.12327) и Wikipedia — «pp. 17–26» (разная пагинация сборника, объём тот же, 10 с.).
- Кандидат на пересказ содержания тех же авторов в открытом доступе: CEUR Vol-1606 paper05 «Application of Constraint-based Technologies in Financial Services» (Felfernig et al., 2016) — Exa отдал фрагменты: filter constraints, incompatibility constraints, MAUT-ранжирование, диагноз несовместимых требований (FastDiag), регрессионное тестирование БЗ «на порядок нескольких сотен ограничений».

- 🟢 **ДОБЫТО.** Браузер → Google Scholar «All 8 versions» (cluster 16926010087011017686) → 5 открытых копий: academia.edu ×2, researchgate ×2, **scholar.archive.org (Wayback авторской страницы TU Graz ist.tugraz.at/felfernig/images/constraint_based_recommendation.pdf)**. curl+UA → **200, 180 273 б, application/pdf**, 10 страниц. Источник всё это время лежал в открытом доступе у автора; «ACM закрыт принципиально» — ложная рамка: закрыт был один канал, а не источник.

```
4ec76d1d397f01e91603e8137a34bf5d85b95134bb04369e6bf77f4ed7feed14  /private/tmp/claude-501/-Users-vasyaevdokimov-repos-personal-finance-dss/a9134b29-56d9-4f88-b692-c70a2d06d50d/scratchpad/fb.pdf
```

#### Полный текст Felfernig & Burke ICEC '08 (pdftotext, дословно)

```text
Constraint-based Recommender Systems:
Technologies and Research Issues
A. Felfernig

R. Burke

Intelligent Systems and Business Informatics
University of Klagenfurt, Austria

College of Computing and Digital Media
DePaul University Chicago, IL, USA

alexander.felfernig@uni-klu.ac.at

rburke@cs.depaul.edu

ABSTRACT
Recommender systems support users in identifying products and
services in e-commerce and other information-rich environments.
Recommendation problems have a long history as a successful AI
application area, with substantial interest beginning in the mid1990s, and increasing with the subsequent rise of e-commerce.
Recommender systems research long focused on recommending
only simple products such as movies or books; constraint-based
recommendation now receives increasing attention due to the
capability of recommending complex products and services. In
this paper, we first introduce a taxonomy of recommendation
knowledge sources and algorithmic approaches. We then go on to
discuss the most prevalent techniques of constraint-based
recommendation and outline open research issues.

Categories and Subject Descriptors
I.2.5. Expert system tools and techniques.

General Terms
Recommender Systems.

Keywords
Constraint-based Recommendation.

1. INTRODUCTION
Although e-commerce is more and more a dominant purchasing
platform, buying complex products and services (e.g., financial
services or computers) online is still a challenging task. Few organizations offer anything beyond simple query interfaces, under
the assumption that customers know the technical details of the
products and services they seek. Recommender technologies [2]
[7] [14] [33] are an attempt to provide automated assistance for
such decision tasks.
When originally developed, recommender systems were
conceived primarily as social systems [21][31] through which
users shared preferences over items (simple products such as
books or movies). These collaborative recommendation
techniques are widely used and actively researched, but the term
recommender systems now refers to a much broader array of
Permission to make digital or hard copies of all or part of this work for
personal or classroom use is granted without fee provided that copies are
not made or distributed for profit or commercial advantage and that
copies bear this notice and the full citation on the first page. To copy
otherwise, to republish, to post on servers or to redistribute to lists,
requires prior specific permission and/or a fee.
10th Int. Conf. on Electronic Commerce (ICEC) ’08 Innsbruck, Austria
Copyright 2008 ACM 978-1-60558-075-3/08/08 ...$5.00.

techniques that share a central focus on providing
recommendations – personalized solution alternatives. We
interpret a recommender system as any system that guides a user
in a personalized way to interesting or useful objects in a large
space of possible options or that produces such objects as output.
This paper highlights one particular technology for
recommender systems: constraint-based recommendation. In this
paradigm recommendation is viewed as a process of constraint
satisfaction [40], some constraints come from users, other
constraints come from the product domain. Products that satisfy
the constraints are good recommendations. This paper situates
constraint-based recommendation within the landscape of
recommendation technologies by characterizing these technologies in terms of their knowledge requirements.
Constraint-based recommendation (see, e.g., [15]) like other
knowledge-based recommendation techniques [6] becomes
important when there are specific requirements that a solution
must meet. Consider the following example:
Joe would like to buy web hosting services for his
business. He connects to a recommender system for such
services and answers a few simple questions such as
whether e-commerce services (e.g., shopping cart or
advisory services) are required, what is the expected
number of users per day, and what is the expected
connection performance. Joe answers these questions and
receives immediate feedback that due to the expected
number of users hosting services should be based on a
higher connection performance (an option that has as well
been selected by many other users). Joe accepts this
proposal and the system recommends the solutions
HostingA and HostingC. Joe asks for more information on
each of these, and learns that they both have similar
pricing, but that although HostingA offers more storage,
HostingC has a larger bandwidth. He ultimately decides
that he would rather have the better bandwidth and
chooses HostingC.
There are a number of ways in which this scenario goes beyond
what could be expected of a purely collaborative system. For
example, a collaborative system requires the accumulation of a
history of choices or product preferences built up over time. It is
these user profiles that are compared to find peer users with
similar tastes, with most techniques requiring at least 20 ratings
for reliability. Collaborative techniques would be unlikely to be
successful for infrequently purchased items: a typical business
owner might make web hosting decisions only once a year or
even less frequently. Further, the kind of explanatory information
(e.g., the repair proposal that is given) that Joe uses in making his

final decision would not likely be found in a purely collaborative
recommender. However, even in this heavily knowledge-based
scenario, collaborative information has its place: information
about what other users have done in similar circumstances is
extremely helpful.
To understand different recommendation approaches and the
role that they can fulfill, it is best to have an overview of the
various kinds of knowledge sources from which recommender
systems can draw. This is the question that we turn to in Section
2. In Section 3, we look at the way that particular choices of
knowledge sources have given rise to the well-recognized types of
recommender systems. Section 4 examines in detail constraintbased recommendation technologies. In Section 5 we discuss
research issues in constraint-based recommendation. With Section
6 we conclude the paper.

2. KNOWLEDGE SOURCES
Like all intelligent systems, recommender systems use different
forms of knowledge. Sometimes this knowledge is implicit, such
as the distribution of user opinions over some group of items or
the knowledge encoded in an algorithm, in other cases it is
explicitly-encoded inferential or ontological knowledge.
There are four sources where the knowledge needed to generate
recommendations can be drawn: from the user herself, from other
peer users of the system, from data about the items being
recommended, and finally from the domain of recommendation
itself, knowledge about how recommended items are used and
what needs they satisfy.
Figure 1 shows a taxonomy of recommendation knowledge that
builds on this commonsense distinction. We follow common
usage in the field and describe as “Content” any type of
knowledge that is not user-generated, although this might be
considered overly broad.

profiles [17][21][32] but other kinds of knowledge can be
considered collaborative as well. In one well-known example,
web links are treated as collaborative votes in the PageRank
algorithm [4]. Demographic data has also been used to draw
similarities between users or to complement rating behavior.
Current research has begun to explore other forms of user opinion
such as social tagging behavior [26] and written reviews [1]. In
the case of our example of web hosting services, collaborative
knowledge might include the opinions of other users on such
services and possibly information about the companies, such as
annual sales or the number of employees.

2.2 User (Individual)
Of course, in order to personalize recommendations, we need
knowledge of the individual user. The relationship between user
and collaborative knowledge can be purely reciprocal, in the
sense that, e.g., Joe's opinions or demographic data are individual
when the system is giving him a recommendation, but social
when another user relies on them.
Historical knowledge of user preferences may be sufficient for
some recommendation tasks, but in many circumstances, the user
will come to the system with a particular intent in mind, and the
recommender system will need to respond to it. These user
requirements may come in different forms.
•

Query: Depending on the user interface, it may be possible
for the user to pose a general query or the interface may
present specific feature/attribute requirements to be
specified. The example above describes such an interface,
which gathers values for specific features, such as the
expected performance of the ISPs Internet connectivity.

•

Constraints: In some recommendation domains, there may
be a variety of types of constraints that a recommended
solution must meet. For example, in the area of rental
apartments, the owner of a German Shepherd would have the
constraint that the landlord must accept large pets. No solution that violates this constraint would likely be acceptable.

•

Preferences: A preference is something that the user would
prefer to be true of the solution, but a solution that violates it
might be acceptable. For example, a buyer may have a
preference for a bottle of wine under $10, but might be
satisfied with a $12 bottle if it were a particularly good deal,
highly appropriate, or if no other alternative existed that
satisfied other, harder, constraints.

•

Context: The user’s context consists of the external
circumstances associated with the recommendation or the
user’s situation. For example, the user’s location might be an
important contextual factor in a restaurant recommendation,
with closer establishments being preferred. The deployment
of context in recommender systems is an area of active
research often borrowing concepts from ubiquitous
computing [34].

Recommendation
Knowledge
Social

Individual

Content

Peer
Opinions

User
Opinions

Item
Attributes

Peer
Demographics

User
Demographics

Contextual
Knowledge

User
Requirements

Domain
Knowledge

Query

Constraints Preferences
MeansEnds

Context
Feature
Ontology

Domain
Constraints

Figure 1: Knowledge Sources in Recommender Systems.

2.1 Collaborative (Social)
Collaborative (social) knowledge is knowledge about other users.
Its most familiar manifestation are numeric rating (opinion)

2.3 Content
The area of content knowledge is very broad. In some cases, a
system will have very little knowledge that can be used to match
users’ needs against products. In an area of personal taste, like
music or fiction, it would be very difficult to reason about the
connection between the user’s mental state and the way in which

items are or are not satisfactory. In other cases, such as the web
hosting example above, there may be considerable scope for
reasoning about the connection between users’ needs and the
available products. The taxonomy distinguishes four different
types of content knowledge.

effective and are generally accepted techniques. Constraint-based
techniques will be discussed in detail in the next section. The
following discussion is a brief overview of the other types.

•

Item attributes: Obviously, the starting point for any type of
reasoning about items must be knowledge about the items
themselves. This may be a simple set of attribute value pairs,
such as might be found associated with a product in a
database, or the item description may itself be structured as
in the case of complex products such as a computer [12].

The approach most closely associated with recommender systems
since the field's inception is of course collaborative filtering or
collaborative recommendation.1 The knowledge sources here are
collaborative opinion profiles, demographic profiles, and user
opinions. Of course one of the strengths of this technique is that
little else is required to implement it in its pure form.

•

Contextual knowledge: Considerable inferential complexity
may be involved in teasing out the consequences of
particular contexts [2]. In the example above, the details of
Joe’s line of business and his customer base may in fact have
significant bearing on the importance attached to his web
site. Contextual factors have been addressed significantly in
only a handful of research and fielded systems. Some mobile
recommender systems for example use location as a
contextual cue.

Many algorithmic approaches have been applied to these
knowledge sources, but in general, the problem can be seen as a
form of multi-way classification task. It differs from classic
classification tasks in that there is no specific dependent class
variable being predicted in all situations, but rather the system
may be called upon to make predictions about any item for any
user. Thus collaborative recommendation is not amenable to a
strict application of the tools of machine learning.

•

Domain knowledge: Finally, a recommender may need to
have deeper knowledge about the products it is
recommending and the uses that they may serve. This
knowledge comes in a variety of forms:
Means-ends knowledge: Means-ends knowledge is perhaps
the most complex component of content knowledge. This is
the inferential knowledge that allows the system to reason
about how particular items (the “means”) satisfy particular
needs or requirements of the user (the “ends”). Such
knowledge could be arbitrarily complex involving physical
reasoning for example, but there are also much more
straightforward formulations, such as the knowledge that a
person interested in a “family car” will typically have a
certain bundle of preferences and constraints, such as
passenger and cargo space [5].
Feature ontology: Item attributes tell a recommender what
features are associated with what products, but often a
recommender will need to know the relationship between
these features: to know, for example, that Ubuntu is a type of
Linux operating system.
Domain constraints: Users have constraints in terms of the
requirements that recommended items must meet, as
described above. The items themselves may also have
constraints that govern their appropriateness in different
circumstances. For example, a particular insurance policy
may only be available to individuals whose are non-smokers,
or as in the Internet services case, the deployment of multimedia content places a limit on the minimum bandwidth a
site will need.

3. RECOMMENDATION TECHNIQUES
For the purposes of this paper, a recommendation technique is a
set of knowledge sources and an algorithmic approach to
generating recommendations using those sources. There are of
course no apriori limitations on how these different sources of
knowledge can be combined, and in fact, the field of
recommender systems has seen great diversity in approaches.
However, certain approaches have turned out to be practical and

3.1 Collaborative Recommendation

The most well-known approach is that of a nearest neighbor, in
which ratings are extrapolated by comparing the user opinion
knowledge against collaborative opinions and extrapolations
made [32]. The popular item-based variant treats the collaborative
information as features associated with items rather than with
users [35]. Model-based techniques have been employed to
compress the collaborative opinion data, including clustering,
singular value decomposition, and others [35].
What all of these methods share is their sole reliance on opinions
or rating data as the knowledge source for recommendations.
There are well-known characteristics that result from this choice.
First, there is positive benefit that no other information about
users or items is required. This makes the approach attractive for
hard to characterize items, like movies and music.
This technique can be said to be the most mature of the
recommendation technologies and the characteristics of these
algorithms are well established. Collaborative recommendation
works best when there is a large amount of collaborative
knowledge available and when there is a substantial history of
user opinion. The density of the collaborative user-item matrix is
a substantial consideration.
Collaborative recommendation can theoretically be applied in any
domain. It places very little restriction on the types of items that
can be recommended and is highly suitable for items in which
user tastes vary for reasons that might be difficult to represent
explicitly, such as music and movies. However, there are
considerations that may make a collaborative approach less
attractive. One is opinion density. A user can listen to dozens of
music tracks in a day, and might watch dozens of movies a year,
but she would unlikely to live in dozens of apartments, own
dozens of cars or have dozens of different pets. In some areas it is
simply more difficult to accumulate a pattern of preference. It is
possible to ask the user to venture a prospective opinion without
having actually experienced the item in question, but such
opinions will generally be quite speculative compared to those
arrived at through experience.
1

The “filtering” terminology is a legacy from an early
application: filtering of interesting Usenet messages [21].

Also, we might expect that decisions regarding items less
frequently purchased will be more sensitive to context. A 10-yearold rating for a car may be completely irrelevant if the user now
has completely different driving patterns due to family and job
requirements. Personal tastes in items such as music do change
over time, but since they are experienced and rated more
regularly, a collaborative system has the possibility of adapting.
The need for a substantial profile of the user gives rise to the
“new user” problem. A new user cannot get much personalized
help from a collaborative system until his profile is sufficiently
large to be used reliably in prediction. A new item is similarly
disadvantaged. It cannot be become a recommendation until some
user rates it, and in general, the system will not have a good sense
for a new item’s appropriateness across the user base until a
number of users have rated it. Together these issues are known as
the “cold start” problem.
The frequency of item churn and the need for freshness are
therefore important considerations. Domains in which items are
rapidly appearing and disappearing will be difficult to handle via
collaborative recommendation because an item might be nearing
the end of its lifetime by the time it gets enough ratings to be
recommended.

3.2 Content-based Recommendation
Content-based recommendation [28] is more like a pure
classification task in the machine learning sense. The task is to
learn a specific classification rule for each user on the basis of the
user's rating information and the attributes of each item so that
items can be classified as likely to be interesting or not. No social
knowledge is used. The content-based problem has been tackled
using a variety of machine learning techniques. However, in
general, some of the more sophisticated techniques have been less
successful, due to the sparsity problem. An individual user profile
may not, in many cases, have enough data for a reliable profile.
Simple techniques such as k-nearest neighbors and naive Bayes
have often proved effective here.
Because a content-based recommender has access to item features
(e.g., keywords or categories), it does not suffer from the new
item problem: new items look just like old items. The new user
problem remains since users must build up a sufficiently rich
profile through the addition of multiple ratings. Depending on the
feature set and learning algorithm, however, a small number of
ratings may be sufficient.
Indeed, the quality of the data set becomes of primary importance
in a content-based system. The learned profiles of each user will
only be as good as the system’s level of detail in representing the
distinctions that matter in the domain. The creators of the music
recommender Pandora (www.pandora.com) first developed a
highly-detailed representation of musical form and expression
before attempting to build a recommender system. Developers
must make sure that all items in the catalog have a uniform,
detailed and complete representation: a combination which can be
difficult to achieve in many e-commerce contexts.

3.3 Knowledge-based Recommendation
Systems that rely on knowledge sources other than those
discussed in Sections 3.1 and 3.2 above are by default known as
knowledge-based recommender systems [6]. Such systems are

characterized therefore by the two knowledge aspects not found in
the other designs: namely user requirements and domain
knowledge. Obviously, there are collaborative and content-based
systems that allow users to pose queries or that have some forms
of heuristics with respect to their content. What distinguishes a
knowledge-based approach is that its emphasis: emphasis on the
user’s situation and how recommended items can meet that
particular need.
Knowledge-based recommender systems are more difficult to
briefly characterize than the other techniques discussed above. If
we consider the taxonomy in Figure 1 and the knowledge sources
used in collaborative and content-based recommendation, it is
clear that the knowledge-based category itself is something of an
accident of history. Systems that used additional knowledge
sources came to be defined as "knowledge-based" because they
relied more heavily on knowledge sources that were not being
employed by the more widely-used techniques.
There are two well-known approaches to knowledge-based
recommendation (case-based recommendation [6] [25] [34] [38]
and constraint-based recommendation [15] [39]. Systems based
on these approaches can exploit all of the knowledge sources
depicted in Figure 1. In terms of used knowledge sources, both
approaches are quite similar. Systems of both types must, for
example, collect the requirements of the current user in order to
derive new solutions, propose repairs in situations where no
solution could be found and support explanations for the
recommended items.
Case-based recommendation treats recommendation as primarily
a similarity-assessment problem. How can the system find a
product that is most similar to what the user has in mind, with the
understanding that what counts as similar will often involve
domain-specific knowledge and considerations. Constraint-based
recommendation takes into account explicitly defined constraints
(e.g., filter constraints or incompatibility constraints). If no item
really fits the wishes of a customer (the calculated similarity value
exceeds a certain threshold for all relevant products or the set of
constraints is inconsistent with the given set of customer
requirements) both knowledge-based approaches exploit
mechanisms supporting the determination of minimal set of
changes to the given set of customer requirements such that a
solution can be found - see, for example, [15] [24].
The interaction with a knowledge-based recommender application
is typically modeled in the form of a dialog (conversational
recommender) where users can specify their requirements in the
form of answers to questions [6] [15] [25] [34] [39]. This dialog
can be modeled explicitly, for example, in the form of a finite
state automaton (see, e.g., [15]) or in a way which allows the user
to select interesting attributes (questions) on her own [25].
Furthermore, user interaction with a recommender application can
be enriched with natural language interaction [39] which allows
for more flexible interaction processes. For example, users can
specify component properties on a textual level without being
forced to answer a potentially larger number of questions.
Another interesting aspect of additional textual interfaces is the
flexibility to support queries which are not directly related to
product search but to issues such as questions regarding the
functionality or technical questions.
Many case-based recommender applications support the concept
of critiquing (see, e.g., [6] [8] [38]), in which the user responds to

a recommended item by identifying how it differs from their
ideal. For example, a user presented with a restaurant featuring a
traditional style of food may apply the critique "More Creative"
and obtain a more contemporary take on the same cuisine [5].
Such an interface has the advantage of allowing the user to
formulate requirements on the fly, in response to examples.
Critiquing interfaces promise a faster identification of interesting
recommendations in terms of less decision effort, better decision
accuracy, and increase of a user’s confidence in a decision [8].
Recent research has moved from unit critiques, in which the user
identifies specific item properties to critique (e.g., “I would prefer
a camera with a lower price”), to more complex compound
critiques, that move along several feature dimensions at once.
Such critiques can be manually engineered (as in [5]) or can be
automatically generated from the existing product assortment by
mining association rules representing representative critique
patterns in the available assortment [38].

3.4 Hybrid Recommendation
A hybrid recommender is one that uses recommendation
components or logic of different types. See [7] for an overview.
For example, a recommender might use both social knowledge
and item features thereby combining collaborative and contentbased approaches. In some sense, the notion of a hybrid is an
artifact of the historical development of recommender system in
which certain types of knowledge sources were exploited first,
leading to well-established techniques that were later combined. If
we view recommendation as a problem the solution to which may
draw on multiple knowledge sources, then the only question to be
answered is which sources are the most appropriate to a given
task and how they can be most effectively used.

4. CONSTRAINT-BASED
RECOMMENDATION
Let us reconsider the recommendation of web hosting services.
The user of the recommender has to provide information about his
personal preferences regarding, for example, the number of
visitors, the need of e-commerce and advisory services, the
maximum price and the required bandwidth for the connection.
On the basis of a given set of user preferences, the recommender
proposes alternative solutions including explanations as to why
those solutions have been proposed. Alternatively, no solution
could have been found by the recommender. In this situation, a
corresponding set of repair alternatives is derived which help the
user to get out of the dead-end. Applications supporting such
recommendation functionalities in many cases build upon
constraint-based technologies [40], where specific product
properties as well as the relationship between customer
requirements and products are modeled in the form of constraints.
Constraint-based approaches typically help to successfully
establish recommenders in domains where items are infrequently
purchased. Furthermore, items are more complex and many
customers do not know all the technical features in detail.
Example product domains range from technical equipment,
financial services, or e-government services to highly complex
products such as production systems or telecommunication
switches. Constraint-based recommenders support customers by
explaining items, automatically proposing repair actions in
situations where no solution can be found, and by proposing

attribute settings based on the preferences of a customer
community thus including collaborative recommendation as well.
The application of constraint-based recommenders in the financial
services domain (recommendation of loans) is shown in [15].
Applications supporting the interactive selling of other types of
financial services are reported in [12]. The core business model of
all those applications is to improve the quality of service for
customers, more specifically the quality of advisory processes.
Those applications have an impact in the sense of, for example,
time savings in advisory sessions due to automated explanation
and repair processes, an increased number of sold products, a
significant reduction of faulty offerings [15].
The authors of [18] present an approach to multimedia-enhanced
recommendation where constraint-based technologies are
additionally equipped with a component supporting item and
component visualization. Thus standard constraint-based
approaches are extended with visualization functionalities letting
users directly interact with the virtual product. Visualization
functionalities provide substantial contributions to user-friendly
interfaces boosting the acceptance of recommenders.

4.1 Recommendation Knowledge
Constraint-based recommendation requires the explicit definition
of questions, product properties and constraints. These elements
constitute a recommender knowledge base which can be represented as a constraint network consisting of two sets of variables
(U, P) and the corresponding constraints (COMP, PROD, FILT).
In this context, customer properties ui ∈ U describe all possible
requirements which can be specified by customers. For example,
max-price = 15 or commerce-services = yes are potential
requirements regarding a web hosting service. Furthermore,
product properties pi ∈ P describe the offered product assortment,
for example: name, price, or supported bandwidth. A simple
example recommender knowledge base is the following:
U={

u1:commerce-services(yes, no),
u2:connection-performance(low, medium, high),
u3:advisory-services(yes, no),
u4:number-users(integer),
u5:maxprice(integer)}

P={

p1:id(integer),
p2:name(text),
p3:commerce-services(yes, no),
p4:price(integer),
p5:available-storage(5GB, 10GB, 20GB, 50GB),
p6:supported-bandwidth(3Mbit, 5Mbit, 10Mbit)}

compi ∈ COMP are (in)compatibility constraints restricting the
set of possible requirements. For example, commerce-services
require a high connection-performance, i.e., a low or medium
connection performance is incompatible with commerce services.
id
comp1
comp2
comp3

constraint
advisory-services require commerce-services.
commerce-services require a high connectionperformance.
a number of expected users (number-users) per day
greater than 250 requires a high connectionperformance.

Table 1: Example Compatibility Constraints.

Such constraints help to assure that customer requirements remain
consistent and that customers learn about specific properties of
the product domain. Furthermore, they help to assure the
consistency of offers posed to customers and thus in many cases
help to decrease costs related to correction processes.
prodi ∈ PROD are product constraints responsible for restricting
the possible instantiations of variables in P. Such constraints can
be seen as compatibility constraints specifically used to
enumerate the offered set of products. Example constraints
representing such products are shown in Table 2.
id

name

prod1
prod2
prod3
prod4
prod5
prod6

HostingA
HostingB
HostingC
HostingD
HostingE
HostingF

commerceservices
yes
no
yes
no
no
yes

advisoryservices

price

storage

yes
no
yes
yes
no
yes

20
10
20
15
5
20

20GB
5GB
10GB
10GB
5GB
20GB

bandwidth
(Mbit/s)
5
3
10
5
3
10

Table 2: Example Product Assortment.
filti ∈ FILT (filter constraints) define the relationship between
customer requirements and products. These constraints represent
rules related to marketing and sales strategies. Example filter
constraints are shown in Table 3 – they describe in detail under
which conditions a certain product should be recommended.
id
filt1
filt2
filt3

constraint
the price of the product has to be lower (equal) than (to) the
maximum price (maxprice) imposed by the customer.
more than 250 visitors per day (number-users) requires a
bandwidth of more than 3Mbit/s.
a high connection-performance is defined by a bandwidth
of more than 3Mbit/s.

Table 3: Example Filter Constraints.

4.2 Dialog Structure
One frequently used approach to the representation of dialog
structures is to explicitly define interaction sequences in which
customers can answer questions [10] [15]. This type of design
exploits the formalisms of finite state automata to explicitly
design the possible states of a recommendation session [10]. A
simple example for such a description is shown in Figure 2.
commerceservices

cs
true
cp

connectionperformance

maxprice

advisoryservices

nu

cp <>
high

cp =
high

Explicitly defined interaction sequences are well-suited for
domains where users do not have a clear opinion about which
questions should be answered next. For example, new sales
representatives in the financial services domain adopt such
interaction mechanisms since those clearly help them to
effectively conduct sales dialogs [15].
In other application domains, customers want to select relevant
and interesting attributes on their own and appreciate personalized
recommendations regarding interesting attributes which trigger
significant time savings regarding the completion of
recommendation sessions [25].

4.3 Calculating Recommendations
On the basis of the definition of a recommendation knowledge
base, we are able to calculate a concrete recommendation for a
customer. The task of deriving recommendations for a customer is
denoted as recommendation task. Given a set of customer
requirements, we can calculate a recommendation (result). A
constraint-based recommender Rconstr is a system that computes
solutions {prodi ∈ PROD} for a given recommendation task.
Definition (Recommendation Task). We define a recommendation
task as a Constraint Satisfaction Problem (CSP) [40] (U, P, CR ∪
COMP ∪ FILT ∪ PROD) where U is a finite set of variables
representing potential requirements of customers and P is a set of
variables defining the basic properties of the product assortment.
Furthermore, CR is a set of customer requirements, COMP
represents a set of (incompatibility) constraints, FILT is a set of
filter constraints, and PROD specifies the set of offered products.
A solution to a given recommendation task (U, P, CR ∪ COMP ∪
FILT ∪ PROD) is a complete assignment to the variables of (U,
P) such that this assignment is consistent with the constraints in
(CR ∪ COMP ∪ FILT ∪ PROD).
Table 4 depicts the requirements {req1, req2, req3, req4, req5} ∈
CR of our example customer (Joe) regarding his web hosting
service solution. Two alternative solutions exist for those
requirements: HostingA (prod1) and HostingC (prod3). On the
basis of these requirements, Joe now for example could decide
that he would rather have the candidate option prod3, i.e., the one
with the better bandwidth (compared to the alternative prod1).
commerceservices
(req1)
yes

true
as

Typically, states correspond to input units of the recommender
application, where specific questions can be posed to customers.
Depending on the answers (preferences) of the customer, one of
the set of possible following states is selected. In our example, the
question regarding the number of users (number-users - nu) is
only posed in situations where customers specify the requirement
of a low or medium connection-performance (cp).

numberusers

advisoryservices
(req2)
yes

connectionperformance
(req3)
high

numberusers
(req4)
500

maxprice
(req5)
20

Table 4: Example Customer Requirements.

4.4 Utilities of Recommendations
true

mp

Figure 2: Example User Interface Description (simplified).

Let us assume our recommender for web hosting services has
knowledge about the major strengths and weaknesses of the
offered products. Those can be specified in terms of their
contribution to the interest dimensions reliability, economy, and
performance. Such dimensions are the basic elements of Multi-

Attribute Utility Theory (MAUT) [41] which is used for
calculating the utility of product alternatives for a specific
customer. In this context, the term utility denotes the degree of fit
between an item the given set of customer requirements.

The question now is which of the two alternative repairs should
be proposed to the customer. For this purpose we can apply the
following formula (Formula 2).

Table 5 depicts scoring rules that define the relationship between
our candidate recommendations (prod1 and prod3) and the defined
interest dimensions. For example, regarding performance,
alternative prod3 is better compared to alternative prod1.

In this context, m denotes the number of different requirements,
utility(r) represents the utility of a repair alternative r, ei is the
interest of the customer in requirement i (importance of
requirement i), and ci(r) (can be 0 or 1) indicates whether requirement i is changed in the current repair alternative r. The values for
ei can be derived by directly asking customers within the scope of
a recommendation session or by learning those preferences from
customer surveys or previous interactions sequences [15]. We
now assume that our customer has the following preferences
regarding the specified requirements (reqi x importance factor):
{(req1’, 0.1), (req2’, 0.4), (req3’, 0.3), (req4’, 0.1), (req5’, 0.1)}.
Interpreting our two example repair alternatives using Formula 2
results in the selection of repair alternative 1 (1/0.4 > 1/0.7)
which should then be proposed to the customer.

product
prod1
prod3

reliability
7
6

economy
7
7

performance
7
9

Table 5: Recommendations and Interest Dimensions.
We can apply the following MAUT utility function in order to
determine the most interesting recommendation for Joe.
utility(x) = Σ(i=1..n) eisi(x)

(1)

In this formula, n denotes the number of interest dimensions,
utility(x) represents the utility of an item x, ei is the interest of the
customer in dimension i, and si(x) represents the contribution of
item x to dimension i. The values for ei can be derived directly
from customer requirements defined within the scope of a
recommendation session [15]. We now assume that Joe is highly
interested in reliability (importance weight of 0.7) and less
interested in economy (importance weight of 0.15) and
performance (importance weight of 0.15). Evaluating the two
product alternatives on the basis of Formula 1 results in the
ranking HostingA (utility=6.8) > HostingC (utility=6.5).

4.5 Explaining Inconsistent Requirements
Table 6 depicts a slightly changed set of requirements {req1’,
req2’, req3’, req4’, req5’} (compared to the definitions in Table4).
commerceservices
(req1’)
no

advisoryservices
(req2’)
yes

connectionperformance
(req3’)
medium

numberusers
(req4’)
500

maxprice
(req5’)
20

Table 6: Inconsistent Customer Requirements.
Obviously, those requirements are inconsistent with our example
set of compatibility constraints (see Table 1) and we have to
support the customer in getting out of this situation. We are
interested in repair actions [15] which indicate interesting and
minimal changes to the requirements (CR) s.t. the calculation of a
recommendation becomes possible.
The calculation of such repairs is based on the concepts of ModelBased Diagnosis [30] which is used to resolve conflicts [19]. In
this context, a conflict is defined as c={reqα, reqβ, …, reqψ} ⊆
CR, s.t. c ∪ COMP ∪ FILT ∪ PROD ∪ U ∪ P is inconsistent. A
conflict c is said to be minimal if not ∃ a conflict c’: c’ ⊂ c. In our
example, alternative repairs resolving the conflicts {c1: (req1,
req2), c2: (req3, req4)} for the requirements shown in Table 6 are
the following (see Table 7).
commerceservices
(**)

advisoryservices (**)

connectionperformance
(**)
medium⇒ high

numberusers
(*)
500

maxprice
(*)
20

no⇒ yes
no

yes
yes⇒ no

medium⇒ high

500

20

Table 7: Repair Alternatives
(* no change possible, **change is possible)

utility(r) = 1/Σ(i=1..m) eici(r)

(2)

4.6 Predicting Attribute Settings
In situations where users do not have detailed technical
knowledge about the product domain and are not able to specify
all relevant requirements, prediction mechanisms support the
identification of potentially useful and interesting attribute
settings. Such predictions could be either calculated on the basis
of explicitly defined rules for deriving default values [15] or
calculated on the basis of already existing interaction sequences
with the recommender application [9].
Using the interaction sequences (history of customer
requirements) of Table 8 we can predict interesting values for
those attributes not already specified by the customer. For this
purpose we can, for example, apply a weighted majority voter
(wmv) [9] (see Formula 3). For each value s of the domain of
attribute uα ∈ {uk+1, uk+2, …, um} we determine its potential
degree of interest for the customer. {u1, u2, …, uk} is the set of
attributes already instantiated by the customer and {uk+1, uk+2, …,
um} is the set of those attributes not instantiated by the customer.
Furthermore, {inst(u1), inst(u2), …, inst(uk)} is the set of
instantiations of the attributes in {u1, u2, …, uk} and [u1i, u2i, …,
umi] is a sequence (vector) of valuations of the attributes {u1, u2,
…, um} in already existing interaction sequences seqi ∈ SEQ
(i=1..n). The potentially most interesting value s ∈ dom(uα) can
be calculated on the basis of the following formula:
wmv(s ∈ dom(uα)) = Σ(i=1..n) (Σ(j=1..k) [inst(uj)=uji])*[uαi=s]. (3)
In this context, i iterates over interaction sequences and j over
already instantiated attributes. We assume that the customer has
already specified the following requirements: {req1: commerceservices=yes, req3: connection-performance=high}. The set SEQ
of already existing interaction sequences is shown in Table 8.
We are now interested in a prediction for the attribute advisoryservices (uα=advisory-services). Applying Formula 3 to the given
setting, results in the recommendation of value yes for the
attribute uα = advisory-services.
Further approaches to the prediction of attribute values take into
account the recommendation of attribute sets not already specified
by the customer and are based on the application of Naïve Bayes
voters. Further details on such approaches can be found in [9].

seqi
1
2
3
4
5

commerc
e-services
(u1)
yes (u11)
yes (u12)
no (u13)
yes (u14)
yes (u15)

connectionperformance
(u2)
medium (u31)
low (u32)
medium (u33)
high (u34)
high (u35)

advisoryservices
(u3)
no (u21)
yes (u22)
no (u23)
yes (u24)
yes (u25)

numberusers
(u4)
100 (u41)
50 (u42)
150 (u43)
200 (u44)
500 (u45)

maxprice
(u5)
15 (u51)
20 (u52)
25 (u53)
25 (u54)
20 (u55)

Table 8: History of Customer Requirements.

s
yes
no

[uαi=s]
0,1,0,1,1
1,0,1,0,0

(Σ(j=1..k) [inst(uj)=uji])
1,1,0,2,2
1,1,0,2,2

Σ(i=1..n)
5
1

Table 9: Calculation of attribute values.

4.7 Selecting Attributes
Another question strongly related to the recommendation of
attribute values is the recommendation of interesting questions,
i.e., questions which a user would like to reply to. Where
traditional entropy-based methods strongly focus on the reduction
of the size of the result set, the aspect of user-centered question
ordering is in many cases not taken into account [25]. In order to
support such functionalities, we need a user interface which
supports the selection of interesting attributes (see, e.g., [25]) and
a corresponding history of user interaction sequences.
A simple approach to the prediction of interesting attributes is
presented in [25]. This approach is based on the measurement of
the frequency of attribute usage (popularity). The popularity of an
attribute can be calculated using Formula 4.
popularity(uα,pos)=#(selections of uα in pos)/#(sessions) (4)
Taking into account the example attribute selection sequences
shown in Table 10, popularity(u1:commerce-services, 1) has the
highest evaluation (0.6). Another approach to select interesting
attributes within the scope of recommendation sessions is to apply
the weighted majority voter (Formula 3) [9] for determining the
next interesting attribute. Thus, the determination of interesting
attribute values is substituted by the selection of interesting
attributes, i.e., in this case the domain under consideration is
represented by a set of different attribute identifiers {u1, u2, …,
un}. In our example, u2 would be selected as the next interesting
attribute (see Table 11) (assuming that {u1, u3} have already been
selected).
i
1
2
3
4
5

attribute1
u1
u1
u1
u2
u2

attribute2
u3
u3
u2
u1
u1

attribute3
u2
u2
u3
u3
u4

attribute4
u5
u5
u4
u4
u3

attribute5
u4
u4
u5
u5
u5

Table 10: History of Selected Attributes.
s
u2
u4
u5

[uαi=s]
0,1,0,0,0
0,0,0,0,1
0,0,0,0,0

(Σ(j=1..k) [inst(uj)=uji])
2,2,1,0,0
2,2,1,0,0
2,2,1,0,0

Σ(i=1..n)
4
0
0

Table 11: Calculation of Interesting Attributes.

4.8 Knowledge Acquisition
In contrast to collaborative and content-based filtering ones,
constraint-based recommenders rely on an explicit knowledge

representation. Changes in the marketing and sales knowledge
have to be immediately updated in the underlying recommender
knowledge base in order to be visible and operable for customers
as well as for sales representatives. Such updates hold the risk of
introducing erroneous definitions which causes faulty recommendations and explanations. In order to support effective development and maintenance processes, we have to provide effective
knowledge acquisition functionalities which support automated
testing and debugging processes.
An approach to the automated generation of test cases for
recommender knowledge bases is documented in [13] where test
cases (examples for correct and faulty recommendations) are
systematically generated from a given user interface description
(represented as a finite state automaton). In this context, heuristics
are presented which help to reduce the number of test cases to be
validated by a domain expert. Concepts from Model-Based
Diagnosis (MBD) [30] are applied in order to identify minimal
sets of changes in the recommender knowledge base such that all
recommendations fulfill the predefined examples. Related
empirical studies presented in [13] report significant time savings
in the identification and repair of erroneous constraints in
recommender knowledge bases.
A similar approach has been developed for the identification of
faulty transition conditions in recommender user interface
descriptions [10] and the identification of faulty scoring rules in
utility constraint sets used for the calculation of item utilities
(which item in the recommendation set has the highest utility for
the customer) [11]. Those debugging and repair concepts have as
well been evaluated within the scope of empirical studies which
clearly show up the potentials for significant time savings in
development and maintenance processes for recommenders.

5. RESEARCH ISSUES
Constraint-based recommendation technologies have successfully
shown their applicability in real-world environments. However,
there exist a number of research issues which have to be tackled
in order to further increase the impact of those technologies.
Consumer Decision Making and Recommender Applications.
Psychological studies [27] have shown that customers do not
exactly know their preferences when confronted with a set of
product alternatives. Typically, preferences are constructed while
learning about the choices offered. In order to successfully deploy
recommender applications in commercial environments we have
to understand the limiting factors customers are subject to when
interacting with a recommender application. On the one hand
need for cognition [23] is a property indicating the extent to
which a user wants to invest time in cognitive efforts related to
the finding of products and services. On the other hand, people
have limited cognitive resources and use heuristics to find optimal
products and services with as little effort as it is possible. This
well known effort-accuracy tradeoff [27] has been observed as
well in online decision situations such as web content search [22].
Both aspects, a persons need for cognition and the effort-accuracy
tradeoff influence the way in which persons try to solve a given
decision making task. Consequently, the design of recommenders
can have a huge impact on how decisions tasks are solved by
customers. In order to take into account such aspects,
psychological theories from the areas of decision theory and
cognitive psychology have to be investigated in detail regarding

their impact on online buying situations. First steps in this
direction are documented in [16].
Complexity Metrics for Recommender Knowledge Bases. The
automated testing and debugging of recommendation knowledge
bases is documented in a number of publications – see, for
example, [10][11][13]. Those techniques help to accelerate error
identification and repair tasks, however, in many cases knowledge
engineers are confronted with different repair alternatives which
help to restore consistency. The question which has to be
answered in this context is which repair alternative should be
recommended. Software engineering research has developed a
couple of complexity metrics which help to effectively identify
faulty parts in given software components. In this context,
knowledge-based systems research should focus on the development of complexity metrics for knowledge bases (in our case
recommender knowledge bases) which help to focus error identification/repair on the most complex parts of a knowledge base.
Community-based Recommendation. Existing recommender
applications are based on knowledge bases created by a small
number of domain experts and knowledge engineers. Future
environments for the development of recommender knowledge
bases will focus on a distributed approach where whole
communities of interest will contribute to the development of a
knowledge base. Such an approach has high potential for
improving knowledge base quality and the effectiveness of related
development and maintenance processes. Such a distributed
paradigm requires changes in underlying development and
maintenance processes (e.g., distributed diagnosis and repair
processes or social network analysis) as well intuitive knowledge
acquisition interfaces supporting end-user development of
knowledge bases.
Recommendation of Configurable Products and Services. Mass
Customization [29] is a paradigm which aims at supporting the
provision of highly variant products and services under the
pricing conditions of Mass Production. In parallel, the increasing
size and complexity of product and service assortments outstrips
the capability of customers to survey it. Especially for highly
variant products and services, the integration of existing
configuration technologies with recommendation approaches is
crucial in order to effectively support customers in their
preference construction processes. The application of
recommendation technologies in this context is manifold, for
example, the recommendation of interesting attribute and
component settings, the recommendation of repair actions, the
recommendation of complete configurations or subconfigurations, or the recommendation of explanations.

6. CONCLUSIONS
Recommender systems employ a wide variety of AI techniques.
These disparate strands of research can be brought together
through an understanding of the knowledge sources on which they
draw. In this paper, we have presented a taxonomy of these
knowledge sources in order to clarify the relationships between
different recommendation techniques.
We have also summarized the most prevalent techniques of
constraint-based recommendation, a recommendation technique
drawing heavily on domain knowledge. This technique is
particularly applicable in complex product- and service domains.
Unlike collaborative and content-based methods, constraint-based

recommendation does not suffer from cold start problems, and can
provide recommendations even for products that are not
purchased or experienced frequently enough to generate a
meaningful history of preferences.

7. REFERENCES
[1] Aciar S., Zhang, D., Simoff, S., and Debenham, J. 2007.
Informed Recommender: Basing Recommendations on
Consumer Product Reviews, IEEE Intelligent Systems
Special Issue: Recommender Systems, 22(3):39-47.
[2] Adomavicius, G. and Tuzhilin, A. 2005. Toward the next
generation of recommender systems: a survey of the state-ofthe-art and possible extensions. IEEE Transactions on
Knowledge and Data Engineering, 17(6): 734-749.
[3] Belkin, N., Kelly, D., Kim, G., Kim, J., Lee, H. Muresan, G.,
Tang, M., Yuan, X., Cool, C. 2003. Query length in
interactive information retrieval, 26th ACM SIGIR
Conference on Research and Development in Information
Retrieval, Toronto, Canada, pp. 205-212.
[4] Brin, S. and Page, L. 1998. The anatomy of a large-scale
hypertextual Web search engine. 7th International WWW
Conference, Brisbane, Australia, pp.107-117.
[5] Burke, R., Hammond, K., and Young, B. 1997. The FindMe
Approach to Assisted Browsing. IEEE Expert, 12(4), pages
32-40.
[6] Burke, R. 2000. Knowledge-based recommender systems.
Encyclopedia of Library & InformationSystems, 69(32).
[7] Burke, R. 2002. Hybrid recommender systems: survey and
experiments. User Modeling and User-Adapted Interaction
12(4):331–370.
[8] Chen, L., and Pu, P. 2006. Evaluating Critiquing-based
Recommender Agents. 21st National Conference on Artificial
Intelligence (AAAI'06), pp. 157-162, Boston, USA.
[9] Coester, R., Gustavsson, A., Olsson, R., and Rudstroem, A.
2002.
Enhancing
web-based
configuration
with
recommendations and cluster-based help’, in AH’02
Workshop on Recommendation and Personalization in ECommerce, Malaga, Spain.
[10] Felfernig, A., Friedrich, G., Isak, K., Shchekotykhin, K.,
Teppan, E, and Jannach, D. 2008. Automated Debugging of
Recommender User Interface Descriptions, to appear:
Journal of Applied Intelligence.
[11] Felfernig, A., Friedrich, G., Teppan, E., and Isak, K 2008.
Intelligent Debugging and Repair of Utility Constraint Sets
in Knowledge-based Recommender Applications, to appear
13th ACM International Conference on Intelligent User
Interfaces, Canary Islands, Spain.
[12] Felfernig, A. 2007. Standardized Configuration Knowledge
Representations as Technological Foundation for Mass
Customization, IEEE Transactions on Engineering
Management, 54(1):41-56.
[13] Felfernig, A. 2007. Reducing Development and Maintenance
Efforts for Web-based Recommender Applications,

International Journal of Web Engineering and Technology,
3(3):329-351.

ITNG ’06 Submissions, 3rd International Conf. on
Information Technology, Las Vegas, Nevada, pp. 388-393.

[14] Felfernig, A., Friedrich, G., Schmidt-Thieme, L. 2007.
Introduction to the IEEE Intelligent Systems Special Issue:
Recommender Systems, 22(3):18-21.

[27] Payne, J., Bettman, J., and Johnson, E. 1993. The Adaptive
Decision Maker. Cambridge University Press.

[15] Felfernig, A., Isak, K., Szabo, K., and Zachar, P. 2007. The
VITA Financial Services Sales Support Environment,
AAAI/IAAI 2007, pp. 1692-1699, Vancouver, Canada.
[16] Felfernig, A., Friedrich, G., Gula, B., Hitz, M., Kruggel, T.,
Melcher, R., Riepan, D., Strauss, S., Teppan, E., and
Vitouch, O. 2007. Persuasive Recommendation: Exploring
Serial Position Effects in Knowledge-based Recommender
Systems, Persuasive 2007, LNCS, 4744.
[17] Herlocker, J., Konstan, J., Terveen, L., and Riedl, J. 2004.
Evaluating collaborative filtering recommender systems.
ACM Transactions on Information Systems, 22(1):5–53.
[18] Jiang, B., Wang, W., and Benbasat, I. 2005. MultimediaBased Interactive Advising Technology for Online
Consumer Decision Support, Communications of the ACM.
48 (9), 93–98.
[19] Junker, U. 2004. QUICKXPLAIN: Preferred Explanations
and Relaxations for Over-Constrained Problems. 19th
National Conference on AI (AAAI’04), pp. 167-172.
[20] Kelleher, J. and Bridge, D. 2004. An Accurate and Scalable
Collaborative Recommender, Artificial Intelligence Review,
21(3-4):193-213.
[21] Konstan, J., Miller, B., Herlocker, J., Gordon, L., and Riedl,
J. 1997. GroupLens: Applying Collaborative Filtering to
Usenet News, Communications of the ACM, 40(3): 77-87.
[22] Kuoa, F., Chub, T., Hsuc, M., Hsieha, H. 2004. An
investigation of effort-accuracy trade-off and the impact of
self-efficacy on Web searching behaviors, Decision Support
Systems, 37: 331-342, Elsevier.
[23] Martin, B., Sherrard, M., Wentzel, D. 2005.The Role of
Sensation Seeking and Need for Cognition on Web-Site
Evaluations: A Resource-Matching Perspective, Psychology
and Marketing, 22(2): 109-126, Wiley.
[24] McSherry, D. 2004. Maximally Successful Relaxations of
Unsuccessful Queries. 15th Conference on Artificial
Intelligence and Cognitive Science, Galway, Ireland, pp.
127–136.
[25] Mirzadeh, N., Ricci, F., Bansal, M. 2005. Feature Selection
Methods for Conversational Recommender Systems, IEEE
International Conference on e-Technology, e-Commerce,
and e-Service (EEE’05), Hongkong, 772-777.
[26] Niwa, S., Doi, T., and Honiden, S. 2006. Web Page
Recommender System based on Folksonomy Mining for

[28] Pazzani, M., and Billsus, D. 1997. Learning and Revising
User Profiles: The Identification of Interesting Web Sites,
Machine Learning. (27), 313–331, (1997).
[29] Pine, B., and Davis, S. 1999. Mass Customization: The New
Frontier in Business Competition. Harvard Business School
Press, 1999.
[30] Reiter, R. 1987. A theory of diagnosis from first principles.
Artificial Intelligence, 23(1):57-95, 1987.
[31] Resnick, P. and Varian, H. R. 1997. Recommender Systems,
Communications of the ACM, 40(8):56-58.
[32] Resnick, P., Iacovou, N., Suchak, M., Bergstrom, P., and
Riedl, J. 1994. GroupLens: An Open Architecture for
Collaborative Filtering of Netnews. ACM Conference on
Computer Supported Cooperative Work, Chapel Hill, NC,
pp. 175–186.
[33] Ricci, F., and Werthner, H. 2006. Special Issue of
International Journal of Electronic Commerce, on
Recommender Systems, 11(2).
[34] Ricci, F. and Q. Nguyen. 2007. Acquiring and Revising
Preferences in a Critique-Based Mobile Recommender
System, IEEE Intelligent Systems Special Issue:
Recommender Systems, 22(3):22-29.
[35] Sarwar, B., Karypis, G., Konstan, J., and Riedl, J. 2001.
Item-based
collaborative
filtering
recommendation
algorithms. 10th International WWW Conference, Hongkong,
pp. 285-295.
[36] Schafer, J., Konstan, J., and Riedl, J. 2000. Electronic
Commerce recommender applications. Journal of Data
Mining and Knowledge Discovery, 5(1/2):115–152.
[37] Simon, H. 1955. A Behavioral Model of Choice. Quarterly
Journal of Economics, 69(1): 99-118.
[38] Smyth, B., McGinty, L., Reilly, J., McCarthy, K. 2004.
Compound Critiques for Conversational Recommender
Systems, IEEE/WIC/ACM International Conference on Web
Intelligence (WI’04), Beijing, China, pp. 145 – 151.
[39] Thompson, C., Göker, M., and Langley, P. 2004. A
Personalized System for Conversational Recommendations.
Journal of Artificial Intelligence Research 21:393–428.
[40] Tsang, E. 1993. Foundations of Constraint Satisfaction,
Academic Press, London and San Diego.
[41] Winterfeldt, D., and Edwards, W. Decision Analysis and
Behavioral Research, Cambridge University Press,
Cambridge,
England,
1986.

```

#### 🔴 Сверка первоисточника с выводом Г16 (§7 `constraint_based_utility_recsys_2026-09-09.md`)
Г16 писал содержание ICEC '08 «с канонических пересказов тех же авторов». Теперь по оригиналу:
1. **Формула MAUT-ранжирования — дословно в оригинале**, §4.4, Formula (1): «utility(x) = Σ(i=1..n) eisi(x) … n denotes the number of interest dimensions, utility(x) represents the utility of an item x, ei is the interest of the customer in dimension i, and si(x) represents the contribution of item x to dimension i. The values for ei can be derived directly from customer requirements defined within the scope of a recommendation session». Пример: веса 0.7/0.15/0.15 → «HostingA (utility=6.8) > HostingC (utility=6.5)». → **строка 5 таблицы §7.1 и фраза «формализованный в 2008 (Felfernig & Burke)» подтверждены первоисточником.** Вывод «новизна по методу умерла» УСТОЯЛ.
2. **База знаний = (U, P) + (COMP, PROD, FILT)**, §4.1 — три класса ограничений. Подтверждает строку 4 таблицы §7.1.
3. **Repair ранжируется по важности изменяемых требований**, §4.5, Formula (2): «utility(r) = 1/Σ(i=1..m) eici(r) … ci(r) (can be 0 or 1) indicates whether requirement i is changed». Конфликт определён как «c={reqα, …} ⊆ CR, s.t. c ∪ COMP ∪ FILT ∪ PROD ∪ U ∪ P is inconsistent» — **ремонтируются ТОЛЬКО требования клиента (CR)**, ограничения COMP/FILT/PROD неприкосновенны. Таблица 7 даже помечает часть требований «* no change possible». → Подтверждает §7.3 п.2 Г16: у школы пустое множество лечится релаксацией требований; случай «пусто из-за нерелаксируемого арифметического ограничения» рецепта не имеет. Зазор УСТОЯЛ. Попутно: Formula (2) — готовый рецепт для нашего пробела «repair при пустом множестве» (строка 13 §7.1): ранжировать варианты ослабления пользовательских параметров по 1/Σ(важность изменённых) — годится для случая, когда пусто из-за ЦЕЛЕЙ пользователя (сроки/суммы), а не из-за Rt≥0 / ПДН.
4. **Объяснения**: §4 «proposes alternative solutions including explanations as to why those solutions have been proposed»; §3.3 «support explanations for the recommended items». Конкретной HOW-формы (вклад веса) в ICEC '08 НЕТ — она у Felfernig & Kiener 2005 и Uta et al. 2024 §4.5.5, как Г16 и записал. Вывод «объяснимость не нова» УСТОЯЛ, опора — не ICEC '08, а 2005/2024.
5. **Финансы в оригинале**: «The application of constraint-based recommenders in the financial services domain (recommendation of loans) is shown in [15]. Applications supporting the interactive selling of other types of financial services are reported in [12]. The core business model of all those applications is to improve the quality of service for customers, more specifically the quality of advisory processes … an increased number of sold products, a significant reduction of faulty offerings». → **объект = продукт продавца, эффект измеряется продажами.** Слов budget / allocation / goal / cash flow / debt в тексте НЕТ (grep по полному тексту — ноль). Подтверждает «зазор по объекту» Г16–Г17 первоисточником, а не пересказом.
6. **Research issues (§5)**: психология решений (effort-accuracy tradeoff, need for cognition, конструирование предпочтений), метрики сложности БЗ, сообщественная разработка БЗ, конфигурируемые продукты. Ни одного пункта про аллокацию собственных средств — «открытая задача» нашего объекта в повестке школы 2008 г. не стоит.
7. **Cold start (§6)**: «Unlike collaborative and content-based methods, constraint-based recommendation does not suffer from cold start problems» — подтверждает строку 987 `recsys_finance_domain_specifics` (там было по Uta 2024).
**Итог по п.1 темы:** выводы Г16–Г17 по существу устояли; меняются две вещи — (а) опора «формализовано в 2008» теперь первоисточник, а не пересказ; (б) запись Г59 «источник однострочный, закрывать нечего» ОШИБОЧНА (10 страниц) и снимается; (в) запись Г16 «ACM DL отдаёт 403, прочитать не удалось» и запись `banks_world_pfm_v2` «⛔ Подтверждено закрытым» — снимаются: открытая авторская копия есть.

### 2. Fano & Kurth 2003 «Personal Choice Point» (IUI '03, pp. 46–52)
- Каналы Г59: ACM → Turnstile; CiteSeerX PDF → 500. Сейчас: Crossref pp. 46–52; S2 CLOSED; Unpaywall is_oa=false, has_repository_copy=false (ложноотрицательный: копия есть).
- 🟢 **ДОБЫТО.** Браузер → Google Scholar «All 5 versions» (cluster 14947868226203220858): scholar.archive.org — Wayback **корпоративной копии Accenture** `accenture.com/NR/rdonlyres/…/tech_pers_choice_iui2003.pdf`; academia.edu. curl+UA → **200, 751 330 б, application/pdf, 8 страниц**. «Нужен один клик человека» (Г59) снимается — клик не нужен.
- sha256 fk.pdf: 674c5503cb8519a9a159599b07f3e973faf1b0b3bb43b8bef85aa77ce199fe47; Felfernig&Burke fb.pdf — выше.

#### Полный текст Fano & Kurth 2003 (pdftotext, дословно)

```text
Personal Choice Point:
Helping users visualize what it means to buy a BMW.
Andrew Fano, Scott W. Kurth
Accenture Technology Labs
161 North Clark
Chicago, Illinois 60601
(312) 693-6606
andrew.e.fano@accenture.com, scott.kurth@accenture.com

ABSTRACT
How do we know if we can afford a particular purchase? We can
find out what the payments might be and check our balances on
various accounts, but does this answer the question? What we
really need to know is how this purchase would affect our other
goals. What do I have to give up to afford this purchase?
Personal Choice Point is a financial planning tool that addresses
these questions by enabling a user to explore the repercussions of
her decisions at the level of her lifestyle goals, not just her
accounts. The user is presented with a graphical representation of
primary lifestyle goals such as home, car, vacation, education, etc.
As the user selects goals and modifies them, it presents the impact
on the user’s life by graphically depicting the impact of a decision
on her other goals. In effect, Personal Choice Point is a planner
that helps restrict the user’s search for a suitable allocation of
resources among goals to the likely set of allocations, from the
much larger space of possible ones. The result is a system that
changes the focus of the user’s task from managing the mechanics
of resource allocation to the evaluation and selection of likely
ones.

Categories and Subject Descriptors
H.5.2 User Interfaces -- Interaction styles, J.1 Administrative
Data Processing – Financial, I.2.8, Problem Solving, Control
Methods, and Search – heuristic methods.

General Terms
Design

Keywords
Recommendation systems, personalization, user modeling, goal
conflicts, visualization, financial planning, decision theory.

1. INTRODUCTION
Suppose you drive a Toyota Camry. Now you’d like to move up
Permission to make digital or hard copies of all or part of this work for
personal or classroom use is granted without fee provided that copies
are not made or distributed for profit or commercial advantage and that
copies bear this notice and the full citation on the first page. To copy
otherwise, or republish, to post on servers or to redistribute to lists,
requires prior speciric permission and/or a fee.
IUI’03, January 12-15, 2003 Miami, Florida, USA
Copyright 2003 ACM1-58113-586-6/03/0001…$5.00

to a BMW. How do you know if you can afford it? Or suppose
you decide to buy a house. Lenders are willing to lend you great
sums, but what will your lifestyle be like when you assume such
debt?
Many tools exist that tell you what your payments will be, but that
doesn’t answer the question. Suppose you learn that a BMW will
cost you an extra $400 per month. What do those extra $400
mean to you? What you really need to know is what the effect of
such a purchase will be on your lifestyle. What are the tradeoffs
with your other goals? What can’t you have if you get the BMW?
While the fact that the BMW will cost an extra $400 is worth
knowing, it doesn’t answer any of these larger questions.
Ultimately it is a lot more meaningful and useful to know that I
will have to, say, downgrade my vacations for a while or postpone
a house purchase for a year.
Personal Choice Point is a financial planning tool that employs a
model of a user’s preferences over competing financial goals to
suggest tradeoffs they might be willing to make. In doing so, the
interaction with the user is changed from managing the mechanics
of accounts - as is typically found in financial planning tools - to
what might be viewed as a conversation with a user about her
lifestyle.
In this paper we describe the user model employed by Personal
Choice Point and the algorithm used to allocate funds. Next, we
discuss the evolution of the interface and the issues that led to
subsequent redesigns
Lastly, we discuss our preliminary
experience with Personal Choice Point, and relate it to other
work. At this point Personal Choice Point is a research prototype
that has not undergone formal evaluation, but has been presented
in numerous industry settings and tested by many people.

1.1. An Example
Let’s take the case of the previously mentioned problem –
upgrading from a Toyota Camry to a BMW. How does Personal
Choice Point go about addressing this issue? Part of the system’s
model of my preferences includes the range of cars I’d consider.
I’d earlier indicated I’d probably never get something less than a
Honda Civic, or more expensive than a BMW 540. I’d also
specified that within this range what I actually expect is
something like a Camry.
In addition to knowing my car preferences, Personal Choice Point
contains a model of my preferences for eight other goals
important to me including vacations, desired home, monthly
savings, monthly spending allowance, furniture, appliances, kids
education, and retirement (throughout this paper we will refer to
such desired spending categories as goals). So I tell Personal

Choice Point that I am changing my car preferences. I now expect
a higher quality car.
My raised expectations means I’m less satisfied than before with
the idea of getting another Toyota Camry – the car I am currently
scheduled to purchase. Consequently Personal Choice Point now
has the task of reallocating my money among the various
competing goals mentioned above in such a way that it will help
address my diminished car satisfaction without becoming overly
dissatisfied with any of my other goals. Note that Personal
Choice Point isn’t trying to save me any money, instead, it’s just
trying to suggest a new allocation of funds among my various
goals with which I’m likely to be content.
Personal Choice Point now takes my newly revised set of
preferences, along with financial information about me and the
cost of my various potential goals, and arrives at a new allocation
of funds between my goals. This new allocation is shown to me
in the form of a graphic depiction of what I can expect to receive
in each of my goals. This allocation is, in effect, the lifestyle that
Personal Choice Point suggests I consider. I am also presented
with a summary of what has changed – the tradeoffs that were
made to accommodate my revised preferences. I learn that yes,
I’m now getting the BMW, but I’ll have to keep my current car
for another 6 months. Moreover, my vacation has been
downgraded from Club Med to camping. And I have to wait an
extra 19 months to afford the kind of house I was planning on
buying. And Personal Choice Point shows me a cheaper furniture
option I might have to consider.
So, can I afford the BMW? Well, if I’m happy with these
changes, then yes, I can. Otherwise I have two choices. I can
revert to my previous set of preferences, or, I can continue
adjusting my preferences for my various goals (e.g. home,
vacation, furniture, retirement, etc) until I arrive at a lifestyle – an
allocation of funds among my various goals - that I am most
satisfied with.

about my different goals, they are not in a position to suggest
reasonable tradeoffs. Therefore rather than focusing on whether a
lifestyle might be right for me, I’ll spend all my time staring at
numbers and trying to figure out where I can draw money from to
be able to support my new car. More likely, however, is that I
won’t bother getting this information at all and end up making a
much less informed decision. It’s almost certain that given the
extra work involved, I would consider far fewer possibilities than
with a tool like Personal Choice Point.

2. PERSONAL CHOICE POINT’S USER
MODEL
The Personal Choice Point prototype contains a model of one
specific user’s preferences for each of nine primary goals
including: home, automobile, vacation, furniture, home
appliance, children’s education, retirement, monthly savings, and
monthly spending allowance.
The user model refers to the set of preferences for these goals.
While each user will include the goals that are relevant to him or
her, what makes Personal Choice Point tractable is that most
people will tend to use a subset of a manageably small set of
goals. Most of the goals listed above, for example, cover the main
spending priorities of a considerable part of the population. But
certainly some will exclude certain goals and include others.
Personal Choice Point’s primary task is to suggest new resource
allocations given a revised set of user preferences. The new
allocation reflects particular tradeoffs with respect to the previous
allocation. The user model employed by Personal Choice Point
was designed to enable certain kinds of tradeoffs to be performed.
Personal Choice Point uses goal, time, and quality tradeoffs
which are described below.

2.1. Goal Tradeoffs

In this case I decide that my vacation is too important to sacrifice.
So rather than revert to my previous set of preferences, I raise the
priority of my vacation goals. It’s not like with cars where I said I
expect a higher quality goal. I still expect the same quality
vacation. I’m just trying to convey to Personal Choice Point that
it should raise the priority of meeting my expectations with
respect to vacations. I’m now less willing to sacrifice vacations.

At the most general level, Personal Choice Point allows users to
trade off across goals. We may decide that furniture is not as high
a priority as, say, cars, so we will want to ensure that our car goals
are addressed more diligently than our furniture goals. If cuts
need to be made we will want Personal Choice Point to tend to
take money from our furniture goal rather than from our car goal.

This revision in my preferences once again results in Personal
Choice Point suggesting a new allocation. So now, yes, I’ve
gotten my Club Med vacation back, but now I’m told I’ll have to
wait even longer for my house, and my allocation to monthly
savings is dropping fast. And I’m still getting my BMW, but now
I have to wait even longer.

2.2. Time Tradeoffs

This interaction -- reviewing Personal Choice Point’s “suggested
lifestyle”, updating my preferences and examining the tradeoffs –
continues until I settle on one I can live with. Just as a good real
estate agent knows what I’m looking for and helps restricts my
search to appropriate homes, Personal Choice Point helps me
navigate through the relatively small space of possible lifestyles
I’d consider, from the much larger space of lifestyles that are
possible.
It is possible, of course, to arrive at the same information using a
spreadsheet or traditional personal finance software. The
difference is that because traditional tools don’t know how I feel

The relative priorities we place on various goals may tell us which
goals are more important, but it is not enough to tell us how to
allocate our resources. There are multiple ways of adding or
withdrawing money from particular goals. One way is to adjust
the expected time of attainment for a goal. For example, we can
postpone or hasten the target date when we intend to buy a car.
Naturally, postponing a purchase gives us more time to save
money for a goal, while hastening it requires additional resources.

2.3. Quality Tradeoffs
In addition to adjusting the time of attainment for a goal, we can
add or remove funds from a goal by adjusting the quality of the
options we choose to satisfy a particular goal. That is, we can
decide to get a cheaper car rather than wait for a more expensive
one.

In sum, we can change the relative priorities between goals, and
then we can also trade off between the time we attain a goal and
the quality of the option we choose for a goal. These tradeoffs are
not possible for all goals because some goals are timeindependent. For example, by definition a user’s monthly
allowance goal and savings goal can’t be hastened or postponed.
They can only be increased and decreased. Similarly, a child’s
education and a planned retirement tend to be pretty fixed in time.
Personal Choice Point relies on three classes of information to
manage these tradeoffs: First, a model of the user’s preferences
over the goals under consideration. Second, information about
the user’s finances and expected changes to income. Lastly,
economic assumptions are made about expected changes to
inflation for various product categories. Our work thus far has
focused primarily on modeling the user’s preferences.

2.4. The User’s Preferences
Personal Choice Point does not try to extract a user’s preferences
by monitoring the user’s activity or other indirect means. Instead,
the user’s preferences are at the forefront of the system. Users
interact with Personal Choice Point by continuously adjusting
their preferences.
The user model consists of the following information:

2.5. Goals
First and foremost is simply the set of goals the user wishes to
address with Personal Choice Point. These goals will typically
include some set similar to the previously mentioned list such as
home, vacation, automobile, etc. Different users might choose to
address a different set

2.6. Goal Priority
Goal Priority is used to adjust for the relative importance of each
goal, as opposed to determining how funds are used to address a
goal. Every goal is assigned a priority between 0 and 1. In
practice, the user does not select a number, but rather estimates a
preference with a slider control. The user never sees numerical
values for any of the preferences we discuss. The precise
numerical values aren’t shown because the meaning of these
preferences lies not in their absolute values, but in the effect on
the resulting lifestyle that changes in the preferences cause.

2.7. Goal Options
Including a goal such as “automobile” simply indicates that we’re
interested in automobiles, but does not identify what kinds of
automobiles we might be interested in. For each type of goal the
user indicates a range of goal options they would plausibly
consider, from the most modest in the worst case to the most
extravagant in the best case. For the automobile goal, for
example, the range of options might be delimited by a Honda
Civic on the low end to a BMW 328 on the high end, rather than a
Yugo and Rolls Royce. After all, it is rather unlikely that
someone who could find himself buying a Yugo might also be in
the market for a Rolls Royce. Therefore restricting the range
eases the users task and helps prevent absurd suggested tradeoffs.
For each of the selected options, the user indicates the option
quality rating qualitatively (using a slider from zero to one e.g.

Civic .3, Camry .6, BMW .9). Importantly, these ratings of the
options are only relevant to other options within the same goal.
They need not be meaningful across goals. Each option also has
an associated cost.

2.8. Time and Quality Expectations
Knowing the range of options a user might consider for a goal
does not tell us what they actually expect and when they expect it.
Moreover, a user’s quality expectations will vary from goal to
goal. For example, someone might plausibly consider a BMW,
but really only expect a far more modest Honda Civic. This same
person, on the other hand, might harbor vacation expectations
closer to the high end of the range of options she has chosen to
include. Consequently, it would be inappropriate to simply aim
for allocations where each goal has options of similar quality. It
is therefore necessary for the user to indicate her quality
expectations for each category. Once again, the user does so
using a slider that indicates a value from zero to one.
Just as quality expectations vary from goal to goal, so do time
expectations. Some goals are simply addressed at different
intervals. People buy cars at different frequencies than vacations.
And some people will keep a car for 15 years, others insist on
changing cars every 2 years. Therefore users indicate their time of
attainment expectations for each of the time-dependent goals.

2.9. Time-Quality Tradeoff Preference
The expectations described above provide a sense of what will
satisfy the user in these ways for each goal. However, what if we
have to choose between the time we attain a goal, and the quality
of the goal option we are attaining? We may be more or less
willing to sacrifice our expectations with respect to quality versus
time. For example, it may be very important to someone to get a
new car every three years and less important to worry about the
class of the car. The user is therefore asked to describe for each
goal the degree (from 0 to 1) to which they tend to favor a higher
quality option versus attaining it sooner. (A value of 1 is a
preference for time expectations, while 0 is for quality.)

2.10. Financial Models
In addition to the user’s preferences Personal Choice Point
employs a financial model including information about the user’s
income and economic assumptions such as the expected rate of
return on investments, and the inflation rate for various goals (e.g.
education, real estate, etc.). Since our research focuses on
enabling users to explore goal tradeoffs, the financial models
included have been developed as far as necessary to support this
objective.

3. The Resource Allocation Algorithm
The problem addressed by Personal Choice Point is essentially a
resource allocation problem: allocate a user’s money among the
user’s goals. For each goal Personal Choice Point must select a
goal option and time of attainment that maximizes the user’s
overall satisfaction .
It is important to establish what we mean by the user’s overall
satisfaction. First and foremost, Personal Choice Point is not
specifically intended to help the user save money. Personal

Choice Point is about how to allocate money, not save it.
Savings, after all, are just another financial goal. The degree to
which income will be reserved for savings is thus treated the same
as other goals.
Satisfaction, therefore, will come from how well the user’s goals
are being addressed, not how much money is being saved. The
degree of satisfaction will vary by goal.
It would be
inappropriate, however, to search for the allocation where the sum
of the goal satisfactions is highest. Such states may correspond to
allocations where some goals are extremely satisfied, while others
are starved. Differences in the importance of goals are accounted
for by normalizing the satisfaction with the user’s goal priority
preferences. Therefore rather than seeking to strictly maximize
satisfaction, the algorithm we use actually seeks to minimize
differences in satisfaction.
The degree of satisfaction for a particular goal is a function of our
time and quality expectations, as well as what our current
allocation indicates we will receive. Generally speaking, we are
satisfied when we get what we expect. We refer to the difference
between an expectation and what we are allocated to receive as
tension. Personal Choice Point therefore seeks to minimize
tension for our various goals. For time-dependent goals we model
the quality tension QT and time tension TT separately. For
example, if we expect a BMW in 14 months but are allocated to
receive a Camry in 21 months there is a time tension and a quality
tension. Users may prefer to have their time of attainment
expectations addressed more or less diligently than their quality
expectations. This preference is represented by Pg a variable
ranging between 0 and 1, where 1 is a total preference for their
time of attainment expectations, and 0 favors their quality
expectations.
Therefore, for a given goal g, the quality tension QTg is simply the
difference between QEg, the quality expectation the user has for g,
and QOg, the user’s rating of the quality of the option currently
allocated for g. This difference is normalized with Pg to account
for the priority the user places on their quality expectations:

QTg = (1 − Pg )(QEg − QOg )
The time tension TTg is calculated in a similar fashion:

 TEg − TOg 

 TSg


TTg = Pg 

Where TEg is the user’s time expectation for g (i.e. the time they
expect to attain g), and TOg is the time of attainment specified in
the current allocation (e.g. the time at which the current allocation
enables us to purchase a Camry). TSg is a goal dependent constant
selected to reflect the time scale within which we typically address
goals of this type. The intent is to capture the fact that, for
example, the time scale at which we buy cars is different than
vacations. In general, the shorter the transaction cycle, the more
sensitive we are to changes in the time of attainment. Time
independent goals such as monthly savings have a Pg of 0.
Finally, goals must be normalized for different goal priorities Ig.
Therefore the overall tension Tg of a time dependent goal g is:

Tg = Ig (TTg + QTg )

3.1. Allocating funds
The allocation algorithm seeks to minimize the differences in
tensions among all goals. Moreover, for each goal, the algorithm
strives to minimize differences between TTg and QTg. The
allocation algorithm is employed whenever a change in the user
model or financial model occurs. The algorithm involves the
following steps:
1.

For each goal g:
Set allocated funds of g to 0.
Set null quality option (i.e. minimum quality)
Set attainment time to TSg (i.e. max attainment time)

2.

Sort goals according to their tension.

3.

Allocate funds to upgrade the goal with the highest tension
where the cost of upgrade is less than the remaining funds.

4.

Resort the goals.

5.

Repeat steps 3 and 4 until funds are exhausted or no further
improvements are affordable for any goal.

Step 3, upgrading a goal, entails making the smallest incremental
improvement to a goal. Time-dependent goals can be improved in
two ways: we can upgrade QOg, the quality of the goal option
(e.g. upgrade from a Toyota Camry to a BMW) or we can
decrement TOg, the time of attainment for the goal (e.g. get the
Camry in 39 months instead of 40 months). While the cost of
these two options are different, the decision is not a financial one.
Instead, it chooses the one that results in a smaller absolute
difference between QTg and TTg – the time and quality tensions
for the given goal. Time-independent goals are far simpler since
they can only be improved by upgrading QOg.
This algorithm does not provably arrive at the allocation with the
minimum difference in tension, but does produce reasonable
approximations. Because the financial models that estimate the
costs of satisfying goals under different conditions are treated as
“black boxes”, it would be impossible to arrive at a provably
optimal state without performing an exhaustive search.
Ultimately, a reasonable approximation is all that is needed. After
all, an optimal solution would only be optimal with respect to a
set of subjective preferences. The value of the algorithm lies not
in its ability to identify optimal states. Instead, given an existing
allocation and a change in the user model or financial data, the
value of the algorithm lies in its ability to produce a new
allocation that reflects a reasonable set of tradeoffs.
Personal Choice Point users do not have strong feelings about the
precise values of their preferences. Instead they recognize
allocations they like. Just as a good real estate agent would not
seek to “prove” that a given house is for me, Personal Choice
Point is not intended to be used to prescribe an outcome given a
user model, but rather simply to guide exploration through the
relatively small space of allocations the user is most likely to
prefer within the much larger space of possible allocations.

4. INTERACTING WITH PERSONAL
CHOICE POINT
To be usable Personal Choice Point must collect the considerable
amount of user information in a manner that is not overwhelming..
Rather than ask the user to enter manually every preference and at
the outset, Personal Choice Point asks the user to provide basic

demographic information and then presents a few default profiles
for the user to adopt. These profiles contain preferences for many
of the most popular goals that can be customized as needed.
While this still involves some work on the part of the user, it is far
simpler than entering everything by hand.
In addition to collecting information, a lot of information must be
presented to the user. The space of possible allocations is quite
large, and each allocation is complex. There are nine goals, each
of which have multiple options, many of which can be fulfilled at
varying times. Conveying these allocations effectively proved to
be quite challenging. We are now on our third interface, having
redesigned and improved the interface as problems have arisen.

More importantly, many of the relationships we’d worked so hard
to present in the second interface missed the point. Knowing
these relationships contributes little to knowing what preferences
to adjust to increase satisfaction. For example, if the current
allocation doesn’t provide a satisfactory car, it doesn’t matter
what the relative priority of the goal is with respect to, say,
furniture. What you know is that you may want to increase the
priority of automobiles. It soon became apparent that what really
needed to be conveyed well is the current allocation and the
changes from the last one. The changes, after all, reflect the
tradeoffs that were made. In the end, it is these tradeoffs that
represent the cost and benefits to the user for any given decision.

Our first interface represented each goal as one picture depicting
the allocated option surrounded by information about the goal
such as the scheduled time of attainment, along with controls that
reflected the user’s preferences for the goal and allowed them to
be adjusted (see Figure 1). As allocations changed, the graphics
for the selected options changed, as well as the values for the time
of attainment.
The problem with this approach proved to be that we had far too
much information present, and too many controls to consider.
While the quality of the goal options was readily apparent, time of
attainment was often lost in the clutter. And there was no way to
see easily other information of potential interest. For example,
while a user could check to see what the priorities were for any
individual goal, there was no way to easily see the relative
priorities of goals.

Figure 2: The second interface
We therefore designed our current interface to present holistically
the user’s entire lifestyle. Each region of the screen once again
corresponds to a particular goal, but the goals together comprise
one scene. Rather than using numbers that would simply be lost
to convey the time of attainment, the transparency of the goal
option is used to convey how distant it is. The farther off the goal
is in time, the less visible it is in the scene. This way, the user can
quickly get a sense of when he will attain his goals. Selecting the
goal presents more precise information.

Figure 1: The initial interface
We decided to present this kind of relative information by varying
the location of the goals on the screen to reflect different
relationships. The second interface allowed the user to plot the
goals according to different criteria, such as goal priority, time of
attainment, and relative changes in the cost of increasing
satisfaction, to name a few (see Figure 2).
While this approach seemed reasonable at the time, the result was
an even more confusing interface. Goals moved about the screen
reflecting a variety of changes. While this looked impressive, so
many changes were occurring, and so many different views were
possible, that it was often quite difficult to understand what was
being shown.
What had initially seemed like a wasted
opportunity – using fixed locations for goals – turned out to have
a key advantage. Users knew where to look to find a given goal.

To highlight the tradeoffs between the previous and new
allocation we employ two strategies. First, rather than simply
displaying the new allocation, goals that undergo a change have
their changes animated in sequence to call attention to the change.
For example, if we change from a Camry to a BMW, the Camry
drives off, and the BMW drives in. Secondly, a list of the
changes is presented. Changes are described in terms of the goal
option that changed (e.g. Vacation declined from Club Med to
Camping) , Home postponed 19 months, etc.).
Figures 3 and 4 show the current interface and illustrate two
allocations. The controls along the bottom of Figure 3 reflect the
user’s preferences for automobiles, the currently selected goal,
and enable the user to update them if so desired. Specifically, the
preferences are presented as “I favor (time vs. quality)” the
priority of the selected goal, and “I expect:” a quality range up to
‘best” and a time range up to “now”. When a user changes a
preference resulting in a new allocation, this control panel is
temporarily replaced by a scrolling list of resulting changes.

Figure 3: The current interface displaying a particular allocation. The controls on the bottom reflect the preferences for
"automobile" the currently selected goal.

Figure 4: A revised allocation after raising the quality expectations for automobiles. The control panel is temporarily replaced to
present the resulting changes

Figure 4 displays an allocation that results from raising the
quality expectations for automobiles. Although it may be hard
to see here, various parts of the scene have changed. For
example, the car has been upgraded to a BMW, the furniture has
been downgraded, the vacation has gone from Club Med to
Camping, and the House has become more transparent,
indicating a longer wait. Some of these changes are visible in
the lower, scrolling panel.

4.1. Initial Experiences with Personal
Choice Point
The current implementation of Personal Choice Point is a
research prototype intended to illustrate and explore how to
enable new services and customer relationships between
financial services companies and their clients. While it is a
working prototype, it is not a deployed system. The current
financial models used are not rigorous enough for actual use.
The intent is for potential clients to adopt this approach and
enter their own financial models. We therefore have not
conducted any formal user studies. Nevertheless, we have
presented Personal Choice Point in its various forms to
numerous clients, internal meetings and conferences. It has
become a very popular tool to explore future directions in
financial services with clients. We have developed a Norwegian
version in response to requests to pursue opportunities in
Europe.
Through informal use it has become clear that users are able to
consider many more potential allocations than they would if
they had to hand choose all of the tradeoffs. Users are most
enthusiastic about having the repercussions of their actions
expressed in terms of changes to other goals. Many people have
remarked that they would have loved to have such a tool
available to them when buying a house because the sums of
money involved were so unfamiliar that they ceased to have
meaning. They had no real way of gauging the implications of
their decisions. After a short period of experimenting with the
system users usually found that they could adjust their
preferences in a manner that led to intuitive and reasonable
tradeoffs.

5. RELATED WORK
Personal Choice Point can be viewed as a kind of recommender
system. Given a user model, Personal Choice Point in effect
recommends a lifestyle - an allocation of funds across the user’s
goals.
Personal Choice Point differs from traditional
recommender systems in important ways. Most recommender
systems don’t consider the impact a recommendation might have
on other user goals. Collaborative filtering techniques are often
used to suggest a particular music CD, book, restaurant, movie,
articles, etc, [5, 6]. In these domains it is not necessary to
consider interference with other goals. However, as we see in
the automobile example discussed earlier, the decisions we make
in one area of our lives can often have very real consequences in
others.
Decision theorists have developed techniques to address the
problem of arriving at decisions when faced with multiple
objectives. For a good overview see 4. Ultimately, the problem
with these approaches is that they rely heavily on a user’s ability
to accurately and consistently assess their preferences.
Moreover, most systems typically need an exhaustive set of

preferences to be elicited from the user before the decision
theoretic techniques can be applied. Some work has explored
the use of incremental elicitation of preferences (e.g. [2, 3]) but
the emphasis is still on the acquisition of accurate user
preferences that enable an outcome to be prescribed. However,
in many cases users are more likely to feel confident in their
assessment of the desirability of an outcome than the particular
preferences upon which the decision was based. In Personal
Choice Point the emphasis is reversed. Rather than accepting an
outcome because you know you have the right preferences, here
we arrive, incidentally, at the “right preferences” because we
recognize an outcome (i.e. an allocation of funds across goals)
as desirable. Personal Choice Point, in other words, is not
intended as a tool that prescribes a particular outcome. Instead,
by turning this into an iterative process, the user collaborates
with Personal Choice Point to arrive at a desirable allocation. In
effect, Personal Choice Point helps the user explore the large
space of potential allocations by using the user’s loosely
specified preferences to restrict it to the small space of likely
allocations. In this respect, Personal Choice Point bears some
similarity to mixed initiative planning systems in which users
cooperate with the system to achieve a desired result [7]. The
process of soliciting a recommendation by modifying a known
state is somewhat similar to the FindMe system [1], which
recommends restaurants in response to users specifying an
example of the restaurant their interested in, but with a change
on a certain dimension (e.g. “I’d like a restaurant like Charlie
Trotter’s but in Denver”).

6. DISCUSSION
Personal Choice Point is not intended to replace current
financial planning applications. Instead it is intended to
complement them and provide a different view of the decisions
being contemplated. Most existing tools such as Quicken, focus
on individual transactions. While financial planning tools do
typically include tools, in these instances it is ultimately up to
the user to specify what goals funds will be added to or removed
from in order to establish a balance. Personal Choice Point
employs the user’s preferences to simulate the likely allocations.
Furthermore, Personal Choice Point does not simply allocate
funds between a static set of options. Instead it dynamically
changes the target options for a goal from the set of plausible
options for that category specified by the user. Because the
mechanics of resource allocation are handled automatically,
many more allocations can be tried and considered in less time.
In the long run, however, we feel the true potential of this
approach lies not only in enabling people to plan multiple goals,
but rather in enabling their execution. For example, a financial
services company that deployed such a tool need not restrict
themselves to planning the purchase of a car. They could
finance and broker the purchase. Naturally this would involve
alliances with many third party service and product providers.
At a time when banks are becoming increasingly commoditized
and reduced to mere lines on a price comparison sites (e.g.
bankrate.com) this approach offers a new differentiator. Rather
than only competing on the basis of who can provide .125%
better rate on a given loan, financial service institutions and
their partners may compete on who can provide their customers
with a better lifestyle. One step we have taken towards
integrating services from potential partners is enabling users to
configure their preferences for Saturn automobiles on Saturn’s

existing web site and incorporate that data into Personal Choice
Point’s model.
More generally, the approach described here is not limited to
personal financial planning. We believe that such goal-oriented
systems can help enable service providers to assume an
important role in their customers’ decision-making process. In
doing so they are not only being helpful to their customers, they
are placing themselves in the position where they can naturally
provide the products and services needed to address their
customers’ goals.

7. REFERENCES
1. Burke, R., Hammond, K., and Young, B. The FindMe
Approach to Assisted Browsing. IEEE Expert, 12(4), pages
32-40, 1997

2. Ha, V., and Haddawy, Problem-Focused Incremental
Elicitation of Multi-Attribute Utility Models. In Proceedings
UAI97, pp 215-222, Aug 1997.
3. Ha, V., and Haddawy, P. Toward Case-Based Preference
Elicitation: Similarity Measures on Preference Structures In
Proceedings UAI98, pp 193-201, July 1998.
4. Keeney, R. L., and Raiffa, H. Decisions with Multiple
Objectives. Cambridge University Press (1993).
5. Lashkari, Y., Metral, M., & Maes, P. Collaborative Interface
Agents. In Proceedings of the Twelfth National Conference
on Artificial Intelligence (Menlo Park, Ca. 1994) 444-449.
6. Miller, B., Riedl, J., and Konstan, J. Experiences with
GroupLens: Making Usenet useful again. Proceedings of the
1997 Usenix Winter Technical Conference. Jan 1997.
7. Veloso, M. M. Towards Mixed-Initiative Rationale-Supported
Planning. In A. Tate (Ed.), Advanced Planning Technology.
Menlo Park, CA: AAAI Press. 1996.

```

#### 🔴 Сверка Fano & Kurth 2003 с выводами Г17, Г59 и канона новизны
Главный вопрос Г17 (стр. 613 `recsys_finance_domain_specifics_2026-09-09.md`): «оптимизирует ли она распределение или только визуализирует последствия. От ответа зависит формулировка зазора новизны». **Ответ по полному тексту: ОПТИМИЗИРУЕТ.** Дословно:
- §3: «The problem addressed by Personal Choice Point is essentially a resource allocation problem: allocate a user's money among the user's goals. For each goal Personal Choice Point must select a goal option and time of attainment that maximizes the user's overall satisfaction.»
- §3: «Savings, after all, are just another financial goal. The degree to which income will be reserved for savings is thus treated the same as other goals.» (резерв = одна из целей, не инвариант — ровно как у Princeton 2024).
- §3: «It would be inappropriate, however, to search for the allocation where the sum of the goal satisfactions is highest. Such states may correspond to allocations where some goals are extremely satisfied, while others are starved … the algorithm we use actually seeks to minimize differences in satisfaction.» Формулы: QTg = (1 − Pg)(QEg − QOg); TTg = Pg·(TEg − TOg)/TSg; Tg = Ig(TTg + QTg).
- §3.1: жадный алгоритм — обнулить, сортировать цели по «tension», апгрейдить самую напряжённую, пока хватает средств; «This algorithm does not provably arrive at the allocation with the minimum difference in tension, but does produce reasonable approximations … it would be impossible to arrive at a provably optimal state without performing an exhaustive search.»
- §4: «Personal Choice Point asks the user to provide basic demographic information and then presents a few default profiles for the user to adopt. These profiles contain preferences for many of the most popular goals» — **предзаданные профили как источник весов**.
- §4: объяснение = список изменений между прошлым и новым распределением: «Vacation declined from Club Med to Camping, Home postponed 19 months».
- §5: «Personal Choice Point can be viewed as a kind of recommender system. Given a user model, Personal Choice Point in effect recommends a lifestyle - an allocation of funds across the user's goals.»
- §2.10: финмодель детерминированная — «expected rate of return on investments, and the inflation rate for various goals»; «developed as far as necessary».
- §4.1: «research prototype … not a deployed system. The current financial models used are not rigorous enough for actual use … we have not conducted any formal user studies»; Норвежская версия; целевой заказчик — финансовые компании (§6: «They could finance and broker the purchase»).
- Долгов как объекта распределения НЕТ: слово debt — один раз, во введении («what will your lifestyle be like when you assume such debt?»). Ни ПДН, ни ограничения ликвидности, ни кризисного режима, ни вероятностной оценки, ни множества ранжированных альтернатив (на каждое изменение предпочтений — ОДНО распределение, пользователь итерирует сам).

**Что это меняет (готовые формулировки вахты):**
1. Г17, итог (стр. ~1040): «Прескриптивного распределения собственного потока [в академической литературе] — ноль … Объект живёт в патентном массиве и отсутствует в академической литературе RS» → **НЕВЕРНО.** Новая: «Прескриптивное распределение собственных денег пользователя между целями, прямо названное рекомендательной системой, опубликовано в 2003 г. (Fano & Kurth, IUI '03, Accenture; прототип без развёртывания и без пользовательской оценки). Долг как объект распределения и нерелаксируемые ограничения платёжеспособности там отсутствуют».
2. Г16 §7.2 «Живо, но слабо — Объект рекомендации … работы, где рекомендуемый объект — аллокация собственных средств пользователя, в добытом массиве не найдены» → **сужается.** Новая: «Внутри школы Felfernig/Burke такой объект не встречается (ICEC '08 проверен по полному тексту: слов budget/allocation/goal нет). Вне школы — есть: Fano & Kurth 2003 (эвристика минимизации разброса «напряжений» целей) и Alaluf et al. 2024 (RL). Остающийся зазор по объекту — ДОЛГ внутри распределения плюс нерелаксируемые инварианты Rt ≥ 0 и ПДН ≤ 0,40».
3. Г59 (стр. 304 `legal_license_tail_2026-09-18.md`): «у Fano & Kurth — распределение ресурса между ЦЕЛЯМИ … совпадает с выводом Г16–17 "зазор по объекту устоял"» → **уточняется**: зазор по объекту устоял только в узкой части (долг + инварианты); «распределение собственных денег между целями как рекомендация» — не зазор.
4. 🔴 Канон `docs/novelty_statement.md` §1, короткая форма: «единственная известная работа, решающая ту же задачу целиком, делает это обучением с подкреплением — то есть чёрным ящиком» → **перестала быть верной в части «единственная»**: Fano & Kurth решают задачу распределения между целями детерминированно и объяснимо (список компромиссов). «Целиком» спасает формулировку только потому, что у них нет долга. Готовая замена: «Известные работы решают задачу распределения либо без долга и без ограничений платёжеспособности (Fano & Kurth 2003 — жадная эвристика, одно распределение на шаг), либо с долгом, но обучением с подкреплением (Alaluf et al. 2024). FINPILOT включает долг и жёсткие инварианты ПДН/ликвидности в допустимое множество, перебирает и ранжирует варианты и показывает вероятностные последствия каждого». Правку живого канона вахта вносит сама по месту (файл не мой — называю адрес: `docs/novelty_statement.md` §1 и §3).
5. Канон §3, строка «Профиль риска как веса критериев — нет»: измерено по патентам; в академическом массиве **предзаданные профили как источник весов целей есть с 2003** (Fano & Kurth §4, default profiles). Ось «риск» у них отсутствует. Строку оставить с уточнением массива.
6. Канон §3, «Вероятностный прогноз последствий», «Жёсткие инварианты», «Множество альтернатив + ранжирование вариантов» — **устояли и против Fano & Kurth** (детерминированная модель; ограничений нет; одно распределение на шаг).
7. Методическая деталь в нашу пользу и против: Fano & Kurth прямо отвергают максимизацию суммы удовлетворённостей («some goals are extremely satisfied, while others are starved») — это аргумент против чистой SAW-свёртки без пола; у нас эту роль играет лексикографический floor-резерв и инварианты. Стоит сослаться в матмодели как на родственное обоснование floor, не как на новизну.

### 3. Инвентарь: какие КОНКРЕТНЫЕ документы по оставшимся доменам числились недобытыми (grep по raw/, 18.09.2026)
Коды замера 86 доменов (`raw-originals/finpilot-data/dead_domains_probe_2026-09-18.tsv`, curl+UA / curl -sk): tochka.com 000/307 · academic.oup.com 403/403 · tgstat.ru 403/403 · data.gov.ru 000/000 · digital.gov.ru 000/000 · papers.ssrn.com 403/302 · eprints.soton.ac.uk 401/401 · acpjournals.org 403/403 · sdmx.oecd.org 403/403 · royalsocietypublishing.org 403/403 · journals.sagepub.com 403/403 · rlms-hse.ru 000/000 · fedresurs.ru 401/401 · infom.ru 000/000 · iso20022.org 403/403 · publication.pravo.gov.ru 000/000.

| Домен | Конкретный документ, числившийся недобытым | Тема / файл | Обойдено ли уже зеркалом |
|---|---|---|---|
| acpjournals.org | Annals Int Med 1996, doi 10.7326/0003-4819-125-7-199610010-00011 | approach_validity (стр. 278, 771, 2051, 2677) | нет → добирать |
| academic.oup.com | статья (стр. 601 approach_validity) — полный текст не добыт | approach_validity | проверить |
| academic.oup.com | QJE 116/4 (Madrian–Shea), QJE 121/2 (Ashraf «Tying Odysseus»), Campbell–Cocco QJE | behavioral_execution_gap, macro_in_forecast | да: NBER w7682, авторское зеркало, NBER WP 9759 → вывод не зависел |
| papers.ssrn.com | SSRN 911512; 2005031; 1591171 (KPT); 1166899 (Das–Markowitz) | approach_validity 2010; calibration_ground_truth 2656; portfolio_theory 775; goal_based 29 | 1166899 — да (Cambridge); остальные проверить |
| journals.sagepub.com | 10.1509/jmr.14.0281; 10.1177/237946151700300203; статья стр. 1922 behavioral_finance_field | behavioral_execution_gap 1611/1865; behavioral_finance_field 1922 | проверить |
| royalsocietypublishing.org | статья стр. 1861 behavioral_finance_field | behavioral_finance_field | проверить |
| eprints.soton.ac.uk | Lessmann (кредитный скоринг) | ml_vs_rules 120/636 | да: зеркало Эдинбурга 200 → вывод не зависел |
| sdmx.oecd.org | корень 403 | open_data_rf_money 607/774 | да: точки API отвечают → вывод не зависел |
| iso20022.org | определения сообщений camt.053 | open_data_rf_money 466 (Г47/Г56) | нет → добирать |
| tgstat.ru | tgstat.ru/finances, /finance | telegram_channel 268/527 | частично: /ratings/channels/economics через Exa |
| data.gov.ru | 🔴 «портал мёртв, канал больше не существует» | open_data_rf_money 23/315/520; data_catalog_build 546/550 (API 401) | нет → проверить вывод |
| tochka.com | tochka.com/self-employed/ | _g49_sub_npd_saas 10/91; Г58 subB | нет → добирать |
| infom.ru | «не резолвится» | open_data_rf_money 29/400 | проверить DNS |
| bankrot.fedresurs.ru | статистика банкротств | market_repackaging 12; аудит 6 | проверить r.jina.ai/Exa |
| digital.gov.ru | reestr.digital.gov.ru/faq; новость о правилах реестра ПО | tails_cbr_mr_software_registry 855–856 | нет → добирать |
| publication.pravo.gov.ru | — | многие темы брали 200 через curl -sk ещё 10.09 | вывод не зависел |
| rlms-hse.ru | сайт проекта | long_horizon 9/195 | да: rlms-hse.cpc.unc.edu 200 → вывод не зависел |

### 4. data.gov.ru
- Последнее упоминание (правило 9): `data_catalog_build_2026-09-17.md` Д1 уже оживил портал — r.jina.ai 200 (199 340 б, «Реестр открытых данных 7,038 наборов»), выгрузка реестра `/portal-back/api/v1/registry/csv|json` → 200 без входа; API наборов `/portal-back/api/v1/dataset/page` → **401 «User not authorized!»** → 🟡 пункт владельцу (регистрация на портале), если понадобятся сами наборы через API.
- Остаток от `open_data_rf_money_2026-09-17.md` стр. 305–315: «формальный текст лицензии недоступен по своему же адресу», «портал мёртв». Проверка: `r.jina.ai/https://data.gov.ru/information-usage` → **200, 1 814 б**, но это оболочка SPA (шапка портала, «Наборы данных · Галерея · Нормативная база …»), текста условий в отрисовке нет. Страница жива; текст условий в SPA грузится отдельно.
- **Вывод open_data «портал мёртв, канал больше не существует» — ОПРОВЕРГНУТ** (уже Д1 data_catalog_build, подтверждаю). Новая формулировка: «data.gov.ru жив; со стороны вахты системный curl рвёт TLS (LibreSSL), r.jina.ai и Python — 200; реестр 7 037 наборов выгружается без входа; API отдельных наборов требует входа (🟡 владелец)». Вывод о пригодности (реестр почти пуст по полям) остаётся за data_catalog_build.

### 5. infom.ru
- DNS через DoH (dns.google): **A 62.122.170.171, NS ns1/ns2.snparking.ru** — домен на парковке регистратора. `dig` локально — таймаут (наш резолвер в туннеле, не сайт). curl 000 · curl -sk 000 · r.jina.ai → 422 «net::ERR_CONNECTION_REFUSED» (сервер отказывает и с их выхода). infom.org.ru → NXDOMAIN.
- 🔴 **Вердикт: НЕДОСТУПЕН по законной причине** — домен припаркован, сервер отклоняет соединение из любых сетей. Не путать с ФОМ: `fom.ru` → 200, 92 229 б. Вывод open_data («материалы инФОМ лежат на cbr.ru») не зависел от домена и устоял.

### 6. reestr.digital.gov.ru и digital.gov.ru (хвост `tails_cbr_mr_software_registry_2026-09-10.md` стр. 820–856)
- `reestr.digital.gov.ru/faq/`: curl+UA **000** · `curl -sk --http1.1` **302 → /help/** (Bitrix, российский УЦ) · r.jina.ai 200 на 213 б с «Target URL returned error 403» (заглушка) · браузер **ERR_CERT_AUTHORITY_INVALID** (российский УЦ, сертификат не ставим). Лечится `-k`: `curl -skL --http1.1 https://reestr.digital.gov.ru/help/` → **200, 379 562 б**, текст 67 453 симв. (сохранён в scratchpad help.txt; выписки ниже дословно).
- Новость `digital.gov.ru/news/pravila-dlya-vklyucheniya-v-reestr-softa-sovmestimost-s-rossijskimi-os`: curl 000 · -k 000 · r.jina.ai 422 TimeoutError. Браузер — ниже.
- Дословно со страницы помощи реестра:
  > «Что необходимо для подачи заявления о включении сведений о ПО/ПАК в Реестр · Подтверждённая учётная запись на Госуслугах · … Квалифицированный сертификат ключа проверки электронной подписи … Срок решения – до 45 рабочих дней со дня регистрации заявления»
  > «Разрешенные и запрещенные компоненты для проверки ПО» — ОС: разрешены «Любые ОС из Реестра · ОС с открытой лицензией · ОС стран, не налагающих санкции», запрещены CentOS, Fedora, RHEL, SUSE, AlmaLinux, Rocky Linux (экспортные ограничения); СУБД: разрешены «Любые СУБД из Реестра · СУБД с открытой лицензией», запрещены Oracle, MS SQL Server, Redis Enterprise, InterSystems Caché и др.; платформы: запрещены «Amazon Web Services · Microsoft Azure …», разрешены «Платформы с открытой лицензией (в частности, .NET Core)»; библиотеки/фреймворки: разрешено «ПО с открытой лицензией (Apache, BSD, MIT и пр.)», запрещено «Любое ПО, имеющее ограничения на распространение или использование на всей территории РФ».
  > Шапка: «Проводятся технические работы. Полноценная работа портала возобновится в ближайшее время.»
- По слову «веб-», «браузер», «облач», «SaaS», «операционн» в тексте помощи — **0 вхождений**. Толкования пп. «м» для веб-приложений на странице помощи НЕТ.
- **Сверка вывода:** tails записал «FAQ недоступен (геоблок) → толкование подтвердить нечем». Теперь: FAQ прочитан, толкования в нём нет → отрицательный результат **подтверждён первоисточником**, вывод tails устоял. Добавка, полезная для роадмапа: наш стек (FastAPI/Python, PostgreSQL, React — открытые лицензии) проходит перечень разрешённых компонентов; развёртывание на AWS/Azure прямо попадает в запрещённые платформы. Подача — Госуслуги + КЭП = 🟡 действие владельца (юрлицо/ИП и подпись).

- 🟢 Новость Минцифры — **браузер** (правила Direct в туннеле + анти-DDoS снимается браузером): вкладка открылась, текст дословно:
  > «19 сентября 2025 … Правила для включения в реестр софта: совместимость с российскими ОС. Москва, 19 сентября 2025 года — Минцифры скорректировало сроки подтверждения соответствия новым правилам для ПО из реестра или претендующего на включение в него. … Совместимость ПО с двумя российскими операционными системами. Требование будет вступать в силу поэтапно, по мере технической готовности разработчиков: с 1 июня 2026 года — для средств виртуализации и офисного ПО; с 1 января 2027 года — для средств обеспечения облачных и распределительных вычислений, хранения данных, серверного ПО, средств управления базами данных, средств обеспечения ИБ; с 1 июня 2027 года — для прикладного и отраслевого ПО, средств обработки и визуализации массивов данных; с 1 января 2028 года — для промышленного ПО и средств управления процессами организации. Соответствие требованиям доверенного ПО. В реестре появится информация о соответствии программы требованиям доверенного ПО. Требования к правообладателям софта. Вводится понятие «контроль» для коммерческой организации… Правообладатели — граждане РФ.»
- **Сверка вывода tails:** вывод «препятствий для ИП/физлица-правообладателя нет» — УСТОЯЛ (новость прямо: «Правообладатели — граждане РФ»). 🔴 **Новое, чего tails не знал:** требование совместимости с ДВУМЯ российскими ОС для прикладного ПО вступает **с 1 июня 2027**. Для FINPILOT (прикладное ПО, веб) это срок: если продукт идёт в реестр, к июню 2027 нужно подтверждение работы на двух ОС из реестра (для веб-приложения на практике — работа сервера и клиента-браузера под Astra/РЕД ОС/ALT и т. п.; толкования для веба у Минцифры по-прежнему нет — отрицательный результат устоял). Готовый вывод для роадмапа «правовой контур»: включение в реестр ПО — не обязательно для запуска; если делать, то до 01.06.2027 или сразу с протоколом совместимости с двумя ОС.

### 7. bankrot.fedresurs.ru / fedresurs.ru
- Коды 18.09.2026: `curl -sk --http1.1` bankrot/ → **401, 1 597 б**; fedresurs.ru/ → **401, 1 597 б**; bankrot/statistics → 200, 2 078 б (SPA-оболочка «EФРСБ», данных в ней нет). r.jina.ai: 200 на 479–485 б с «Target URL returned error 401… maybe requiring CAPTCHA». Exa fetch /statistics и fedresurs.ru/news → CRAWL_LIVECRAWL_TIMEOUT. Браузер (вкладка 43) → «403 Error Forbidden. Access to bankrot.fedresurs.ru is forbidden … IP: 79.104.4.214».
- 🔴 **Разбор 401: это НЕ форма входа.** Тело 401 дословно — защита **Qrator** (`/__qrator/qauth_utm_v2d_v9118.js`), «Пожалуйста, пройдите проверку. Ваш IP-адрес: 79.104.4.214», поле «Enter captcha». То есть 401 = антибот с капчей, а браузер получает жёсткий 403 по IP. Прежняя запись «401 → нужен логин владельца» (market_repackaging стр. 12, аудит № 6) неверна по классу.
- **Вердикт:** 🟢/🟡 смешанный — сайт жив; наш адрес 79.104.4.214 в блоке Qrator. Лечится сменой выходного IP (другой провайдер/мобильная сеть владельца) или прохождением капчи человеком → 🟡 «один клик/смена сети владельца». Вкладку 43 закрываю: там не капча, а жёсткий 403 по IP — кликать нечего.
- **Сверка вывода:** market_repackaging (1.C, стр. 814–905) взял числа банкротств (568 тыс. судебных + 68,3 тыс. внесудебных за 2025; ~1 152 плана реструктуризации за I пг 2025) из статбюллетеней Федресурса, опубликованных вне этого домена; вывод «пул есть, предмета продажи нет» от домена не зависел — УСТОЯЛ.

### 8. tochka.com/self-employed/ (Г49, Г58)
- Коды 18.09.2026: curl+UA **000** · `curl -sk --http1.1` → 307 + cookie ipp_uid/ipp_key; с cookie-jar → **200, 86 281 б, но тело = JS-проверка** (`<meta http-equiv="refresh" content="10;URL=/ciez2a">`, обфусцированный скрипт) — заглушка, не данные · r.jina.ai → 200 на 311 б «Target URL returned error 403» (ip 34.96.49.229, заглушка антибота) · Wayback CDX → единственный снимок 2022-11-30 (устарел; availability API 429) · Exa search — официальной страницы Точки для самозанятых не выдал (выдал Т-Банк и обзоры тарифов РКО) · браузер chrome-devtools и playwright → **ERR_CERT_AUTHORITY_INVALID** · headless Chrome из Bash с `--ignore-certificate-errors` (не установка сертификата, аналог `curl -k`) → повис без вывода, 0 б, процесс снят.
- **Вердикт:** 🟢 исполнимо, не сделано — нужен клиент, который одновременно исполняет JS и игнорирует российский УЦ. Инструмента под рукой, который это делает, в этой сессии нет: chrome-devtools/playwright MCP запускаются без флага игнорирования сертификата. Решение без владельца: добавить в конфиг playwright MCP `--ignore-https-errors` (это не установка корневого сертификата) — пункт вахте в очередь инструментов.
- **Сверка вывода:** последнее упоминание — Г58 subB, стр. 177: «Точка Самозанятые: партнёр ФНС, чеки, справки, доходы в ФНС» + платёжный календарь с прогнозом «по операциям за предыдущие 4 месяца» (справка Точки 2024) — взято вторичными каналами и Exa (`allo.tochka.com/kassovyi-razryv`, `/persaccounting/`). Вывод Г49 («у банков для самозанятых — налоговый контур, а не распределение личного потока») от страницы /self-employed/ не зависел — УСТОЯЛ; недобытым остаётся только точная цена/тариф для самозанятого-физлица у Точки.

- Уточнение: headless Chrome с `--ignore-certificate-errors` всё же успел сбросить DOM (260 б) — это **страница блокировки антибота** («sid: 776 · id: sodAYKBnna61 · ip: 79.104.4.214 · datetime 2026-09-18 13:50:54»), тот же формат, что у r.jina.ai (ip 34.96.49.229). То есть JS исполнен, сертификат пройден, но антибот Точки (Variti-подобный) режет и headless, и прокси. Остаётся только обычный (не headless) браузер с игнорированием сертификата либо человек → 🟡 «открыть страницу владельцем в своём браузере и сохранить текст», если понадобится тариф. Для выводов не требуется.

### 9. iso20022.org — определение camt.053 (Г47, Г56; хвост `bank_statement_corpus_pass4` стр. 528, `_g59_sub_tail_list_b` E4)
- Коды: curl+UA 403 / curl -sk 403 (замер 86 доменов); **браузер** `iso20022.org/iso-20022-message-definitions?search=camt.053` → открылся сразу: «camt.053 · 1 Message Set · Bank-to-Customer Cash Management · LAST UPDATED 19 March 2026 · DOWNLOAD COMPLETE MESSAGE SET». Скачивание изнутри страницы `fetch('/message/<id>/download')` → **200**: `camt.053.001.14_0.xsd` 110 035 б; `camt.052.001.14_0.xsd` 110 037 б; `camt.054.001.14_0.xsd` 107 246 б; `camt.060.001.07.xsd` 27 199 б. Шапка: «Generated by Standards Editor on 2026 Mar 02 17:31:00». Полный комплект (MDR+MUG) — `https://www.iso20022.org/message-set/1246/download`.
- Структура (разбор XSD, 177 complexType, дословные имена элементов и кратности):
  - `Document` → `BkToCstmrStmt:BankToCustomerStatementV14` → `GrpHdr[1..1]`, `Stmt:AccountStatement15[1..n]`.
  - `AccountStatement15`: Id[1], StmtPgntn, CreDtTm, FrToDt, `Acct:CashAccount43[1..1]`, `Intrst[0..n]`, `Bal:CashBalance8[1..n]`, `TxsSummry`, `Ntry:ReportEntry16[0..n]`.
  - `CashBalance8`: Tp[1], `CdtLine[0..n]` (кредитная линия), Amt[1], CdtDbtInd[1], Dt[1], Avlbty.
  - `ReportEntry16` (операция): NtryRef, **Amt[1..1]**, **CdtDbtInd[1..1]**, RvslInd, Sts[1], **BookgDt**, **ValDt**, AcctSvcrRef, **BkTxCd[1..1]** (код типа операции, Domn/Prtry), Chrgs, Intrst, `CardTx:CardEntry5`, NtryDtls[0..n], AddtlNtryInf.
  - `EntryTransaction16`: Refs, Amt, CdtDbtInd, AmtDtls (инструктированная/валютная сумма, курс), BkTxCd, Chrgs, Intrst, **RltdPties** (Dbtr/Cdtr/UltmtCdtr…), **Purp**, **RmtInf (Ustrd Max140Text[0..n] / Strd)**, **CardTx:CardTransaction18**, Tax, RtrInf, AddtlTxInf.
- **Сверка вывода:** pass4 (стр. 528) закрыл вопрос отрицательно для ГОСТ Р ИСО 20022-1 («выписк» 0, camt 0) и оставил «искать сообщение camt.053.001.xx в Репозитории» — теперь найдено, актуальная версия **.001.14** от 02.03.2026. Вывод pass4 «ГОСТ бесполезен, нужен репозиторий» УСТОЯЛ. 🔴 Практический вывод для бэкенда (готовый, не развилка): каноническая модель операции FINPILOT совместима с camt.053 по полям Amt+CdtDbtInd+BookgDt/ValDt+BkTxCd+RltdPties+RmtInf.Ustrd+CardTx.MCC; если внутренняя схема транзакции хранит ровно эти поля (плюс знак через CdtDbtInd, а не отрицательную сумму), импорт camt.053 от ~71 банка с iBank (pass4 стр. 637) — адаптер, а не переделка. E4 (retail-профиль CAMT.053 в РФ, стандарты Банка России на основе ISO 20022) этой темой не закрыт — остаётся в работе вахты (🟢).

### 10. tgstat.ru (telegram_channel стр. 268, 466, 527 — вход в П1–П2)
- Браузер `tgstat.ru/finances` (вкладка 45) → Cloudflare **Turnstile** «Verify you are human», Ray ID a3d0d9b7699b6fac. Exa fetch /finances и /ratings/channels/finances → CRAWL_UNKNOWN_ERROR.
- r.jina.ai (18.09.2026, без UA): `/finances` → **200, 4 578 б, «Страница не существует - 404»** (TGStat сам отдаёт 404); `/ratings/channels/finances` → 404 так же; `/economics` → **200, 32 647 б, «Telegram-каналы / Россия / Экономика»** (полный список); `/business` → **200, 34 082 б, «Бизнес и стартапы»**; корень и `/ratings/channels/economics` → Cloudflare 403 (прокси пропускают не все пути).
- 🔴 **Вывод:** адреса `tgstat.ru/finances` и `/finance`, записанные в telegram_channel как «недобытые», **не существуют** — за Cloudflare стояла страница 404. Категории «Финансы» у TGStat нет; финансовые каналы лежат в «Экономике» (её Г30.4 уже взял через Exa с числами) и частично в «Бизнес и стартапы». Вывод Г30.4 («допущение ~30 % подписчиков опровергнуто», по рейтингу «Экономики») УСТОЯЛ и опирается на правильную категорию. Вкладку 45 закрываю, несмотря на Turnstile: клик человека откроет 404, пункт владельцу бессмыслен.

### 11. Пейволл-издатели — список конкретных недобытых статей (после сверки по последнему упоминанию)
Уже обойдено в своих темах (вывод не зависел, повтор не нужен): royalsocietypublishing.org — Vadillo et al. 2018 взят с LSE eprints (200, gold OA); SAGE — Hagger et al. 2016 взят с KU Leuven (200, bronze OA); SSRN 2005031 — Gathergood & Weber взят как CFCM WP 12/04 (200); SSRN 1166899 — Das et al. через Cambridge; OUP QJE (Madrian–Shea, Ashraf, Campbell–Cocco) — NBER/авторские копии.
Остались недобытыми (каждый — с выводом, который на нём висел):
- A. DeMiguel, Garlappi, Uppal 2009, RFS 22(5) (OUP; SSRN 911512) — approach_validity §4.3/Д: «три числа (14 моделей / 7 наборов; "gain … offset by estimation error"; окно ~3000/6000 мес.) дословно не подтверждены, цитировать нельзя»; portfolio_theory стр. 776–778.
- B. Fleming & DeMets 1996, Ann Intern Med 125(7):605–613 (acpjournals) — «цитировать нечем, только библиографическая ссылка».
- C. Netemeyer, Warmath, Fernandes, Lynch 2018, JCR 45(1):68–89 (OUP; SSRN 3485990 GREEN) — Д.6.5 «ОТКАЗ».
- D. Kritzman, Page, Turkington (SSRN 1591171) — portfolio_theory стр. 775 «KPT full text не получен».
- E1. Brown & Lahey 2015 «Small Victories», JMR 52(6):768–783 (SAGE) — behavioral_execution_gap стр. 1865.
- E2. Grinstein-Weiss et al. 2017 R2S/TurboTax (SAGE, Behavioral Science & Policy 3(2)) — стр. 1611: «только абстракт».

#### A. DeMiguel, Garlappi, Uppal 2009 — ✅ дословно подтверждено
- Google Scholar в браузере (вкладка 46) → **reCAPTCHA «google.com/sorry»** — 🟡 один клик владельца, вкладка оставлена открытой: `https://www.google.com/sorry/index?continue=https://scholar.google.com/scholar%3Fq%3D%2522Optimal%2Bversus%2Bnaive%2Bdiversification%2522%2BDeMiguel…`. OpenAlex: oa_status closed, локации — doi.org и RePEc (submittedVersion). CiteSeerX PDF 10.1.1.334.8547 → 404.
- Exa search → аннотация **опубликованной версии** в трёх независимых выдачах (CiteSeerX summary 10.1.1.334.8547; scispace с издательской строкой «The Author 2007. Published by Oxford University Press on behalf of The Society for Financial Studies»; бюллетень SUFE с DOI 10.1093/rfs/hhm075) — текст совпадает дословно:
  > «We evaluate the out-of-sample performance of the sample-based mean-variance model, and its extensions designed to reduce estimation error, relative to the naive 1/N portfolio. Of the 14 models we evaluate across seven empirical datasets, none is consistently better than the 1/N rule in terms of Sharpe ratio, certainty-equivalent return, or turnover, which indicates that, out of sample, the gain from optimal diversification is more than offset by estimation error. Based on parameters calibrated to the US equity market, our analytical results and simulations show that the estimation window needed for the sample-based mean-variance strategy and its extensions to outperform the 1/N benchmark is around 3000 months for a portfolio with 25 assets and about 6000 months for a portfolio with 50 assets. This suggests that there are still many "miles to go" before the gains promised by optimal portfolio choice can actually be realized out of sample. (JEL G11)»
- Тело статьи (копия на scribd.com/document/1037352684, фрагмент через Exa), введение: «Based on parameters calibrated to US stock-market data, we find that the critical length of the estimation window is 3000 months for a portfolio with only 25 assets, and more than 6000 months for a portfolio with 50 assets. The severity of estimation error is startling if we consider that, in practice, these portfolio models are typically estimated using only 60 or 120 months of data.» и условия: «(i) the estimation window is long; (ii) the ex ante (true) Sharpe ratio of the mean-variance efficient portfolio is substantially higher than that of the 1/N portfolio; and (iii) the number of assets is small.»
- 🔴 **Вывод меняется:** approach_validity («три числа дословно не подтверждены и в выводы темы в таком виде идти не должны; ссылаться только как на факт существования») → **все три числа подтверждены дословно по аннотации опубликованной версии** — цитировать можно. Сам вывод «оценочная ошибка съедает выигрыш оптимизации; простое правило устойчивее» от этого не меняется, а получает опору. Встречная позиция тоже зафиксирована в выдаче: Kritzman, Page, Turkington 2010 (оптимизация выигрывает при длинных окнах оценки средних) и Kirby & Ostdiek («When does the 1/N rule work?» — проигрыш MV в DGU объяснён дизайном исследования).

#### C. Netemeyer, Warmath, Fernandes, Lynch 2018 (JCR 45(1):68–89) — ✅ аннотация, шкала и числа добыты
- Каналы: OpenAlex closed (doi.org + RePEc hdl); RePEc `ideas.repec.org/a/oup/jconrs/v45y2018i1p68-89` — «Access to full text is restricted to subscribers» (тело статьи — 🟡 пейволл OUP). Открыто через Exa: аннотация опубликованной версии (RePEc и репозиторий Católica Lisbon `ciencia.ucp.pt`, совпадают дословно), шкала — SJDM DMIDI, расширенный тезис ACR (scispace PDF).
- Аннотация дословно: «Though perceived financial well-being is viewed as an important topic of consumer research, the literature contains no accepted definition of this construct. Further, there has been little systematic examination of how perceived financial well-being may affect overall well-being. Using consumer financial narratives, several large-scale surveys, and two experiments, we conceptualize perceived financial well-being as two related but separate constructs: 1) stress related to the management of money today (current money management stress), and 2) a sense of security in one's financial future (expected future financial security). We develop and validate measures of these constructs (web appendix A) and then demonstrate their relationship to overall well-being, controlling for other life domains and objective measures of the financial domain. Our findings demonstrate that perceived financial well-being is a key predictor of overall well-being and comparable in magnitude to the combined effect of other life domains (job satisfaction, physical health assessment, and relationship support satisfaction). Further, the relative importance of current money management stress to overall well-being varies by income groups and due to the differing antecedents of current money management stress and expected future financial security.»
- Шкала (10 пунктов, 1–5, SJDM DMIDI дословно): Expected Future Financial Security — «I am becoming financially secure. I am securing my financial future. I will achieve the financial goals that I have set for myself. I have saved (or will be able to save) enough money to last me to the end of my life. I will be financially secure until the end of my life.» Current Money Management Stress — «Because of my money situation, I feel I will never have the things I want in life. I am behind with my finances. My finances control my life. Whenever I feel in control of my finances, something happens that sets me back. I am unable to enjoy life because I obsess too much about money.»
- Расширенный тезис ACR (те же авторы): «Current money management stress was predicted by traits and behaviors that are negative and more short-term oriented: making only minimal payments, lacking in self-control, and being materialistic. Behaviors and traits that reflect longer-term thinking, such as planning for money long-term and a willingness to take investment risk, were related to future financial security … collectively explained 33% (Study 4) and 39% (Study 5) of the variance in well-being … the effect of current money management stress on well-being is stronger for low-income individuals, and … the effect of future financial security is stronger for younger individuals … financial literacy showed a small negative partial effect on perceived future financial security, and had no effect on money management stress.»
- 🔴 **Вывод меняется (усиливается, не переворачивается):** approach_validity §2.2 стоял на сниппете, Д.6.5 запрещал цитировать. Теперь рамка «два раздельных конструкта с разными антецедентами» подтверждена дословно — запрет снимается. Новое, чего в теме не было: **«making only minimal payments» — прямой антецедент стресса управления деньгами**, т. е. долговая часть нашей рекомендации (минимальные платежи против досрочного погашения) бьёт в ПЕРВЫЙ конструкт, а резерв/цели — во второй. Формулировка approach_validity «наша целевая функция бьёт преимущественно во второй конструкт» → уточнение: «долговой блок (уход от минимальных платежей) работает на первый конструкт, резерв и цели — на второй; одна SAW-свёртка нагружается на оба, и это проверяемо шкалой из 10 пунктов». Готовое решение для роадмапа «продукт/данные»: шкала Netemeyer (10 пунктов, 2 подшкалы) — инструмент измерения эффекта в опросе волны 2/3, без ML.

#### B. Fleming & DeMets 1996 (Ann Intern Med 125(7):605–613) — ✅ аннотация издателя добыта; тело — 🟡 пейволл
- Коды прежние: curl+UA 403 5 785 б, -sk 403 5 849 б, r.jina.ai 200 на 514–519 б (заглушка «Just a moment»), Wayback 404; аудит № 6: браузер — Cloudflare «Just a moment», после reload проверка осталась (вкладка 15, чужая). OpenAlex — closed; PubMed «No abstract available».
- **Exa search** вернул страницу издателя `acpjournals.org/doi/10.7326/0003-4819-125-7-199610010-00011` отрисованной (краулер Exa проходит Cloudflare): раздел «Perspectives», «Get Access» — тело за пейволлом ACP; **аннотация на странице издателя есть**, дословно:
  > «Phase 3 clinical trials, which evaluate the effect that new interventions have on the clinical outcomes of particular relevance to the patient (such as death, loss of vision, or other major symptomatic event), often require many participants to be followed for a long time. There has recently been great interest in using surrogate end points, such as tumor shrinkage or changes in cholesterol level, blood pressure, CD4 cell count, or other laboratory measures, to reduce the cost and duration of clinical trials. In theory, for a surrogate end point to be an effective substitute for the clinical outcome, effects of the intervention on the surrogate must reliably predict the overall effect on the clinical outcome. In practice, this requirement frequently fails. Among several explanations for this failure is the possibility that the disease process could affect the clinical outcome through several causal pathways that are not mediated through the surrogate, with the intervention's effect on these pathways differing from its effect on the surrogate. Even more likely, the intervention might also affect the clinical outcome by unintended, unanticipated, and unrecognized mechanisms of action that operate independently of the disease process. … Surrogate end points can be useful in phase 2 screening trials … In definitive phase 3 trials, except for rare circumstances in which the validity of the surrogate end point has already been rigorously established, the primary end point should be the true clinical outcome.»
- **Пейволл-разметка acpjournals.org:** открыто — страница статьи, аннотация, реквизиты, список литературы («References»); за пейволлом — PDF и полный текст («Get Access»).
- 🔴 **Вывод меняется:** approach_validity Д.6.4 «абстракт не депонирован ни в MEDLINE, ни в EuropePMC — добыть хотя бы дословный абстракт технически невозможно … процитировать нечем, только библиографическая ссылка» → **неверно по факту: аннотация есть на странице издателя и теперь добыта дословно.** Цитировать можно; оба режима отказа, которые тема выводила из сниппета (путь мимо суррогата; непредусмотренный механизм вмешательства, «unintended, unanticipated, and unrecognized mechanisms»), подтверждены первоисточником. Аналогия темы «SAW-полезность — суррогат благополучия; план "резерв → в долг" поднимает полезность и снимает устройство самоконтроля» опирается ровно на второй режим — УСТОЯЛА и получила опору. Замена «через NCBI Bookshelf IOM 2010» больше не обязательна.

#### D. Kritzman, Page, Turkington 2010 (FAJ 66(2):31–39; SSRN 1591171) — аннотация была, добавлена авторская ретроспектива; тело — 🟡 Turnstile/пейволл
- SSRN: `curl -sk` 403 5 782 б; r.jina.ai 200 на 491 б «Just a moment … requiring CAPTCHA»; браузер (вкладка **47**, оставлена открытой) → Cloudflare **Turnstile** «Verifying…», Ray ID a3d0e2eb3d0ef495 → 🟡 один клик владельца: `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1591171`.
- Exa: аннотация (совпадает с уже записанной в portfolio_theory §2.1) + 🟢 **новый первоисточник — ретроспектива самих авторов (State Street, одностраничник)** `globalmarkets.statestreet.com/…/in_defense_of_optimization_-_one_page.pdf`, дословно: «In our 2010 paper, we argued that such studies had a fatal flaw: in their effort to systematize historical testing of optimal portfolios, they used implausible trailing 5-year returns for assets as the expected returns for those assets going forward. … We ran new tests with extremely simple, but plausible, expected returns. Now, textbook mean-variance optimization added plenty of value out-of-sample by recognizing the different risk levels of assets and their varying potential for diversification. The result held across asset classes, industry portfolios, factor portfolios, and individual stocks.»
- **Сверка вывода** portfolio_theory (стр. 432–441, 695–697: «удар приходится по компоненте входа, оцениваемой по короткой выборке») — УСТОЯЛ; теперь стоит на аннотации + авторской ретроспективе, а не на аннотации + вторичном конспекте.

#### E1. Brown & Lahey 2015 «Small Victories» (JMR 52(6):768–783) — ✅ ПОЛНЫЙ ТЕКСТ финальной версии
- Прежде: SAGE закрыт, авторская копия `people.tamu.edu/~alexbrown/papers/smallvictories.pdf` → 404 (behavioral_execution_gap стр. 1866). Причина 404 — **не тот адрес**: сайт автора переехал на `alexbrownecon.com`, в `research.html` ссылка «final version» → `https://people.tamu.edu/~alexbrown/papers/small_victories.pdf` (с подчёркиванием) → curl+UA **200, 1 330 985 б, application/pdf**, 2 672 строки текста; sha256 8532e46d2b979bc8988048e835daf5408852a83651e9fc40ac34c7615f359ace. Заголовок — журнальный («…Task Completion and Debt Repayment»).
- Дословно (введение): «we show in our final section that it will only be useful to borrowers in specific cases of debt reduction where interest rates between loans do not differ greatly. In the event of large differences in interest rates on loans, it will be best for consumers to pay off debts from highest interest rate to lowest, despite the additional motivational benefit from the small-victories approach.» Также: «Those with higher self-control, better critical reasoning skills, and higher risk aversion … benefit more from having chosen ascending … the people least in need of this intervention are the ones most likely to benefit from it.»
- Дословно (финальный раздел): «subjects in the ascending ordering, on average, complete a cell in 11.08 seconds compared to 12.50 seconds in the descending ordering … about 13% more productive than descending. We caution that these results should not be used to make definitive conclusions about debt-reduction situations … Suppose an individual has two $10,000 outstanding loans. The first loan is at 10%, and the second has a rate between 10% and 20%. … for all interest rates 16% and below, this individual would pay back both loans faster following the small victories method … But for rates 17% and higher, the conventional economic method … still produces faster debt repayment … For rates 12% and lower … a lower amount spent on loans … In general, this method works best when individuals have debts with similar interest rates.»
- **Сверка вывода:** behavioral_execution_gap (стр. 1876–1900 и 1308–1322) сверял WP с журналом только по аннотациям и деке CFPB и оговаривал «построчной сверки журнальной статьи не было». Теперь: числа 11,08/12,50 с, +13 %, порог 16/17 % и 12 % в финальной версии **совпадают** с теми, что тема взяла из WP. Вывод «snowball оправдан только при близких ставках; при большом разрыве — avalanche» УСТОЯЛ и подтверждён финальным текстом; оговорка «сверки не было» снимается. Для матмодели (Avalanche-фильтр) — опора, не изменение.

#### E2. Grinstein-Weiss et al. 2017 (R2S/TurboTax; Behavioral Science & Policy) — ✅ ПОЛНЫЙ ТЕКСТ рабочей версии
- SAGE (журнал) — пейволл; r.jina.ai давал только аннотацию и список литературы (стр. 1611). Открытая версия — CSD Working Paper 17-29, WUSTL Open Scholarship `openscholarship.wustl.edu/cgi/viewcontent.cgi?article=1049&context=csd_research`: curl+UA **403, 5 754 б** (Cloudflare); **Exa fetch → полный текст** («A published version of this study is forthcoming in Behavioral Science & Policy»).
- Дословно, Эксп. 1 (N = 646 116, TurboTax Freedom Edition, сезон 2015, средний доход ≈ $15 055, средний возврат $2 030), Table 2: «Percent who saved: Control 8.44% · Emergency Savings 13.34%*** · Interactive Goals 12.60%*** · Interactive Retirement 12.40%***; Mean amount saved: $160.25 · $243.76 · $229.52 · $228.26». «participants who received the emergency savings intervention were significantly more likely to deposit to savings accounts than were participants who received the future savings interactive message χ2 = 30.14, p < .001 and retirement savings interactive message, χ2 = 48.56, p < .001 … interactive retirement … deposited an average of $68 more … Cohen's d = 0.07 … In total, the net increase in the refund saved due to treatments was $35,625,127.» Предыстория: «In a previous iteration of the R2S project … varying a suggested impetus for saving (general goals, retirement, or emergencies) had no influence on savings deposit behavior.» Эксп. 3: «MChoice Architecture = $340.68, MControl = $190.91, t(549) = 2.63, Cohen's d = .22 … Savings Emphasized … $174.75 … p > .25».
- **Сверка вывода** behavioral_execution_gap Д11.3.6 (🟡, «только абстракт»): вывод «архитектура выбора работает, одно упоминание сбережений — нет, нужен сильный акцент или "без трения"» УСТОЯЛ и теперь с числами по рукам. 🟢 Новое для продукта (готовый вывод, не развилка): формулировка «на непредвиденные расходы» (emergency) дала больше всех (+4,9 п.п. доли сберегающих против +4,0–4,2 у «целей» и «пенсии»), но размер эффекта на сумму мал (d = 0,07); рычаг — не текст, а расположение варианта «в резерв» первым и в один клик. Для экрана рекомендации FINPILOT: вариант с резервом ставить первым пунктом, подпись — «подушка на непредвиденное», а не «цель».

### 12. Разметка пейволл-издателей: что открыто, что закрыто (замер 18.09.2026)
| Издатель | Коды (curl+UA / -sk / r.jina.ai / браузер) | Что ОТКРЫТО | Что за ПЕЙВОЛЛОМ | Как брали |
|---|---|---|---|---|
| academic.oup.com (RFS, JCR, QJE) | 403 / 403 / заглушка / **Turnstile** на странице статьи (вкладка 48, Ray a3d0eb0b8acbd155; корень в аудите № 6 открывался) | аннотации (через RePEc, CiteSeerX, репозитории вузов, Exa), метаданные | полный текст и PDF статей RFS/JCR/QJE (RePEc: «Access to full text is restricted to subscribers») | NBER/авторские копии, RePEc, Exa |
| journals.sagepub.com (JMR, BSP, PPS) | 403 5 784 б / 403 / 200 для аннотации и списка литературы / Cloudflare проходит («Verification successful», по Exa) | аннотация, список литературы; статьи с OA-статусом bronze/gold | полный текст закрытых статей (JMR 2015, BSP 2017) | авторские финальные версии (Brown), WP вуза (WUSTL), Unpaywall-репозитории (KU Leuven) |
| royalsocietypublishing.org (RSOS) | 403 5 754 б / 403 / — / корень открывается (аудит № 6) | **ВСЁ**: Royal Society Open Science — gold OA, CC BY 4.0; мешал только антибот, пейволла нет | ничего | Unpaywall → LSE eprints 200 |
| acpjournals.org (Ann Intern Med) | 403 5 785 б / 403 5 849 б / заглушка 514–519 б / Cloudflare не проходит и после reload (аудит № 6) | страница статьи, **аннотация**, реквизиты, References — всё видно краулеру Exa | полный текст и PDF («Get Access») | Exa search (отрисованная страница издателя) |
| papers.ssrn.com | 403 / 302→403 / «requiring CAPTCHA» / **Turnstile** (вкладка 47) | аннотации (через Exa и зеркала) | ничего по праву — SSRN бесплатен; мешает только Turnstile → 🟡 один клик владельца | зеркала, Exa |
| dl.acm.org | 403 / 403 / заглушка / **Turnstile** (Felfernig ICEC '08 — FREE ACCESS, т. е. пейволла нет) | аннотации, метаданные; у FREE ACCESS статей — и PDF после клика | обычные статьи ACM без FREE ACCESS | авторские копии через scholar.archive.org (Wayback) |

---

## 🔴 КАКИЕ ВЫВОДЫ ИЗМЕНИЛИСЬ

| # | Тема / файл | Прежняя формулировка | Новая формулировка | Чем подтверждено |
|---|---|---|---|---|
| 1 | 🔴 Г17 `recsys_finance_domain_specifics` (итог, ~стр. 1040) | «Прескриптивного распределения собственного потока [в академ. литературе] — ноль … объект живёт в патентном массиве и отсутствует в академической литературе RS» | «Прескриптивное распределение собственных денег между целями, прямо названное рекомендательной системой, опубликовано в 2003 г. (Fano & Kurth, IUI '03): жадная эвристика минимизации разброса "напряжений" целей, предзаданные профили, объяснение через список компромиссов. Долга как объекта распределения и нерелаксируемых ограничений платёжеспособности там нет» | полный текст Fano & Kurth (§2 этого файла) |
| 2 | 🔴 Г16 `constraint_based_utility_recsys` §7.2 «Объект рекомендации» | «работы, где рекомендуемый объект — аллокация собственных средств пользователя, в добытом массиве не найдены» | «внутри школы Felfernig/Burke — не найдены (ICEC '08 по полному тексту: budget/allocation/goal — 0); вне школы — есть (Fano & Kurth 2003; Alaluf 2024). Остающийся зазор по объекту — долг внутри распределения + нерелаксируемые Rt ≥ 0 и ПДН ≤ 0,40» | §1, §2 |
| 3 | 🔴 канон `docs/novelty_statement.md` §1, короткая форма | «единственная известная работа, решающая ту же задачу целиком, делает это обучением с подкреплением — то есть чёрным ящиком» | «Известные работы решают задачу распределения либо без долга и без ограничений платёжеспособности (Fano & Kurth 2003 — жадная эвристика, одно распределение на шаг), либо с долгом, но обучением с подкреплением (Alaluf et al. 2024). FINPILOT включает долг и жёсткие инварианты ПДН/ликвидности в допустимое множество, перебирает и ранжирует варианты и показывает вероятностные последствия каждого» — **правку живого канона вносит вахта** (адрес: `docs/novelty_statement.md` §1 и §3, строка «Профиль риска как веса» — уточнить массив) | §2 |
| 4 | Г59 `legal_license_tail` стр. 302 | «Felfernig & Burke — одностраничный тезис туториала ("pages 3"); закрывать нечего» | «статья 10 страниц (Article No. 3, pp. 1–10, Crossref), полный текст добыт; содержание подтверждает Г16: MAUT-формула дословно, ремонт только требований клиента, финансы = продажа продуктов» | Crossref + PDF (§1) |
| 5 | Г59 стр. 304 | «Fano & Kurth: нужен один клик человека; зазор по объекту устоял» | «клик не нужен (копия Accenture в Wayback); зазор по объекту устоял только в узкой части (долг + инварианты)» | §2 |
| 6 | Г16 шапка; `banks_world_pfm_v2` стр. 492 | «ACM DL отдаёт 403, прочитать не удалось»; «⛔ Подтверждено закрытым» | «открытая авторская копия есть (scholar.archive.org ← ist.tugraz.at)» | §1 |
| 7 | `approach_validity` §4.3 / Д.6.3 (DeMiguel 2009) | «три числа дословно не подтверждены, цитировать нельзя» | «все три числа (14 моделей / 7 наборов; "gain … more than offset by estimation error"; ~3000 / ~6000 мес.) подтверждены по аннотации опубликованной версии — цитировать можно» | §11A |
| 8 | `approach_validity` Д.6.4 (Fleming & DeMets 1996) | «абстракт не депонирован нигде — добыть технически невозможно, цитировать нечем» | «аннотация есть на странице издателя, добыта дословно; оба режима отказа суррогата подтверждены первоисточником» | §11B |
| 9 | `approach_validity` §2.2 / Д.6.5 (Netemeyer 2018) | «из сниппета, дословность не подтверждена; цитироваться не должны» | «рамка двух конструктов подтверждена дословно + шкала 10 пунктов; уточнение: "making only minimal payments" — антецедент стресса управления деньгами, значит долговой блок работает на ПЕРВЫЙ конструкт, резерв/цели — на второй» | §11C |
| 10 | `open_data_rf_money` стр. 23/315 (уже поправлено `data_catalog_build` Д1) | «data.gov.ru мёртв, канала больше не существует» | «жив; реестр выгружается без входа; API наборов — 401 (🟡 регистрация владельца)» | §4 |
| 11 | `market_repackaging` стр. 12; аудит № 6 | «fedresurs.ru 401 — требует сессии (форма входа)» | «401 = Qrator-капча, не логин; браузер — 403 по IP 79.104.4.214 → 🟡 смена сети/клик владельца» | §7 |
| 12 | `tails_cbr_mr_software_registry` стр. 820 | «FAQ реестра недоступен (геоблок)» | «FAQ прочитан (`-k`): толкования для веба нет — отрицательный результат подтверждён; новое: совместимость с двумя российскими ОС для прикладного ПО с 01.06.2027; наш стек (открытые лицензии) проходит перечень разрешённых компонентов, AWS/Azure — запрещённые платформы» | §6 |
| 13 | `telegram_channel` стр. 268/527 | «tgstat.ru/finances — не добыто (403)» | «такой страницы нет (404 за Cloudflare); финансовые каналы — категория "Экономика", уже взятая Г30.4» | §10 |

**Устояли без изменений (источник добыт, вывод подтверждён):** Г16 «новизна по методу/объяснимости умерла»; Г16 §7.3 п.2 «единственный методический зазор — нерелаксируемые инварианты»; KPT/DGU в portfolio_theory; Brown & Lahey «snowball только при близких ставках» (финальная версия совпала с WP); R2S «архитектура выбора работает, одно упоминание — нет»; ISO 20022 (pass4: «нужен репозиторий, не ГОСТ»); Г49/Г58 по Точке; market_repackaging по банкротствам; infom.ru (домен припаркован).

## Остаток по трём классам (правило владельца 18.09.2026)
- 🔴 **НЕДОСТУПЕН (поломка сайта):** `infom.ru` — домен на парковке (NS snparking.ru), сервер отклоняет соединение из любой сети, включая r.jina.ai. `rlms-hse.ru` — NXDOMAIN (зеркало `rlms-hse.cpc.unc.edu` живо, вывод не зависел).
- 🟡 **Действие владельца:**
  1. Один клик Turnstile/reCAPTCHA — вкладки оставлены открытыми: **46** `https://www.google.com/sorry/…` (Google Scholar), **47** `https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1591171` (KPT), **48** `https://academic.oup.com/rfs/article/22/5/1915/1592901` (DeMiguel RFS). Для выводов клики НЕ нужны (всё взято другими каналами) — только если понадобится полный текст журнальной версии.
  2. fedresurs.ru / bankrot.fedresurs.ru — наш IP 79.104.4.214 в блоке Qrator: открыть страницу из другой сети (мобильный интернет) и пройти капчу.
  3. data.gov.ru — регистрация на портале, если понадобится API отдельных наборов (реестр отдаётся без входа).
  4. Реестр ПО Минцифры — Госуслуги + КЭП, если решим подаваться (срок совместимости с двумя ОС для прикладного ПО — 01.06.2027).
  5. Пейволл (деньги/подписка): полные тексты OUP (RFS 2009, JCR 2018), ACP (Ann Intern Med 1996), SAGE (JMR 2015 журнальная вёрстка) — для выводов не требуются.
- 🟢 **Наша работа, не сделана:** `tochka.com/self-employed/` — нужен НЕ-headless браузер с игнорированием российского УЦ (headless режется антиботом; MCP-браузеры падают на сертификате); предложение вахте: флаг `--ignore-https-errors` в конфиге playwright MCP. Retail-профиль camt.053 у Банка России (E4 Г59) — в работу вахты.

## ВЫЖИМКА Г60
1. Главный пункт: Felfernig & Burke ICEC '08 — **10 страниц, а не одностраничник**, открытая авторская копия (Wayback TU Graz) добыта целиком. Вывод Г16 «новизна по методу умерла» подтверждён первоисточником: MAUT-формула дословно, ремонт только требований клиента, финансы = продажа продуктов банка.
2. 🔴 Fano & Kurth 2003 добыт целиком (копия Accenture, клик не нужен) и **сужает новизну по объекту**: распределение собственных денег между целями как рекомендация опубликовано в 2003 г., детерминированно и объяснимо. Остающийся зазор — долг внутри распределения + нерелаксируемые Rt ≥ 0 / ПДН ≤ 0,40 + перебор и ранжирование вариантов + вероятностные последствия.
3. 🔴 Канон `docs/novelty_statement.md` §1 (короткая форма «единственная известная работа — RL») перестал быть верным; готовая замена — в разделе «какие выводы изменились», п.3. Правка живого канона — за вахтой.
4. approach_validity: три источника переведены из «цитировать нельзя» в «подтверждено дословно» (DeMiguel 2009, Fleming & DeMets 1996, Netemeyer 2018); у Netemeyer новое — «минимальные платежи» кормят стресс управления деньгами, то есть долговой блок бьёт в первый конструкт, резерв/цели — во второй.
5. Brown & Lahey (финальная версия) и R2S (рабочая версия, числа по рукам) — выводы устояли; из R2S готовое решение для экрана: вариант «в резерв» первым, подпись «на непредвиденное».
6. ISO 20022 camt.053.001.14 (02.03.2026) скачан через браузер; модель операции FINPILOT должна хранить Amt+CdtDbtInd+BookgDt/ValDt+BkTxCd+RltdPties+RmtInf+MCC — тогда импорт camt — адаптер.
7. Реестр ПО Минцифры: веб-толкования нет (подтверждено по FAQ); новое — требование совместимости с двумя российскими ОС для прикладного ПО с 01.06.2027.
8. Классы отказов уточнены: fedresurs 401 = Qrator-капча (не логин); tgstat /finances = несуществующая страница; data.gov.ru жив; infom.ru — единственный новый честный «НЕДОСТУПЕН» (парковка домена).
9. Итог по оси А для этого списка: 🔴 2 (infom.ru, rlms-hse.ru), 🟡 5 пунктов владельцу (3 клика, смена сети, регистрация/КЭП, пейволл по желанию), 🟢 2 пункта работы вахты (Точка, E4 camt retail).
10. Подагентов: 0. Каналы: браузер chrome-devtools (7 вкладок, 4 закрыты, 3 оставлены с капчей), Exa (9 поисков, 4 fetch), curl/-k/r.jina.ai, Crossref/OpenAlex/S2/Unpaywall/DoH.

