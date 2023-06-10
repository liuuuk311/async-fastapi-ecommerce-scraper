--
-- PostgreSQL database dump
--

-- Dumped from database version 14.1 (Debian 14.1-1.pgdg110+1)
-- Dumped by pg_dump version 14.1 (Debian 14.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: search_brand; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.brand (created_at, id, is_active, name, description, description_it, description_en, logo, is_hot) FROM stdin;
2022-03-31 11:38:40.180058+00	3	t	FrSky	FrSky	FrSky	FrSky	frsky.jpeg	f
2022-03-31 11:41:11.536486+00	5	t	BETAFPV	BETAFPV	BETAFPV	BETAFPV	betafpv.jpg	f
2022-04-05 09:18:37.167176+00	1	t	TBS	Team Blacksheep - Serious Toys	Team Blacksheep - Serious Toys	Team Blacksheep - Serious Toys	tbs.jpg	t
2022-04-05 09:18:51.010473+00	2	t	iFlight	iFlight - Where dreams can fly	iFlight - Where dreams can fly	iFlight - Where dreams can fly	iflight.png	t
2022-04-05 09:20:33.904308+00	4	t	CaddxFPV	Caddx FPV	Caddx FPV	Caddx FPV	Caddx.jpg	f
\.


--
-- Data for Name: search_continent; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.continent (created_at, id, is_active, name, name_en, name_it) FROM stdin;
2021-12-18 06:02:31.291079+00	1	t	Asia	Asia	Asia
2021-12-18 06:02:31.294318+00	2	t	America	America	America
2021-12-18 06:02:31.29599+00	3	t	Africa	Africa	Africa
2021-12-18 06:02:31.297524+00	4	t	Europe	Europe	Europa
2021-12-23 09:42:48.901123+00	5	t	Oceania	Oceania	Oceania
\.


--
-- Data for Name: search_country; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.country (created_at, id, is_active, name, continent_id, name_en, name_it) FROM stdin;
2021-12-18 06:02:47.415593+00	1	t	Italy	4	Italy	Italia
2021-12-18 06:02:47.420881+00	2	t	France	4	France	Francia
2021-12-18 06:02:47.42507+00	3	t	Belgium	4	Belgium	Belgio
2021-12-18 06:02:47.429293+00	4	t	Germany	4	Germany	Germania
2021-12-18 06:02:47.433612+00	5	t	Greece	4	Greece	Grecia
2021-12-18 06:02:47.438239+00	6	t	San Marino	4	San Marino	San Marino
2021-12-18 06:02:47.4424+00	7	t	Luxembour	4	Luxembour	Lussemburgo
2021-12-18 06:02:47.446554+00	8	t	Netherlands	4	Netherlands	Olanda
2021-12-18 06:02:47.450629+00	9	t	Spain	4	Spain	Spagna
2021-12-18 06:02:47.454526+00	10	t	United Kingdom	4	United Kingdom	Regno Unito
2021-12-18 06:02:47.458517+00	11	t	Austria	4	Austria	Austria
2021-12-18 06:02:47.465006+00	12	t	Denmark	4	Denmark	Danimarca
2021-12-18 06:02:47.469821+00	13	t	Finland	4	Finland	Finlandia
2021-12-18 06:02:47.475474+00	14	t	Ireland	4	Ireland	Irlanda
2021-12-18 06:02:47.481091+00	15	t	Portugal	4	Portugal	Portogallo
2021-12-18 06:02:47.486511+00	16	t	Sweden	4	Sweden	Svezia
2021-12-18 06:02:47.493249+00	17	t	Bulgaria	4	Bulgaria	Bulgaria
2021-12-18 06:02:47.498256+00	18	t	Croatia	4	Croatia	Croazia
2021-12-18 06:02:47.502377+00	19	t	Cyprus	4	Cyprus	Cipro
2021-12-18 06:02:47.506639+00	20	t	Czech Republic	4	Czech Republic	Repubblica Ceca
2021-12-18 06:02:47.510943+00	21	t	Estonia	4	Estonia	Estonia
2021-12-18 06:02:47.515176+00	22	t	Hungary	4	Hungary	Ungheria
2021-12-18 06:02:47.519315+00	23	t	Latvia	4	Latvia	Lettonia
2021-12-18 06:02:47.523588+00	24	t	Lithuania	4	Lithuania	Lituania
2021-12-18 06:02:47.528084+00	25	t	Malta	4	Malta	Malta
2021-12-18 06:02:47.532455+00	26	t	Poland 	4	Poland 	Polonia
2021-12-18 06:02:47.537999+00	27	t	Romania	4	Romania	Romania
2021-12-18 06:02:47.542784+00	28	t	Ukraine	4	Ukraine	Ucraina
2021-12-18 06:02:47.547433+00	29	t	Slovakia	4	Slovakia	Slovacchia
2021-12-18 06:02:47.551698+00	30	t	Sloveni	4	Sloveni	Slovenia
2021-12-18 06:02:47.556243+00	31	t	Albania	4	Albania	Albania
2021-12-18 06:02:47.56065+00	32	t	Bosnia	4	Bosnia	Bosnia
2021-12-18 06:02:47.564992+00	33	t	Israel	4	Israel	Israele
2021-12-18 06:02:47.569501+00	34	t	Iceland	4	Iceland	Islanda
2021-12-18 06:02:47.573686+00	35	t	Liechtenstein	4	Liechtenstein	Liechtenstein
2021-12-18 06:02:47.577703+00	36	t	Macedonia	4	Macedonia	Macedonia
2021-12-18 06:02:47.581701+00	37	t	Moldova	4	Moldova	Moldavia
2021-12-18 06:02:47.586362+00	38	t	Montenegro	4	Montenegro	Montenegro
2021-12-18 06:02:47.591226+00	39	t	Norway	4	Norway	Norvegia
2021-12-18 06:02:47.595838+00	40	t	Serbia	4	Serbia	Serbia
2021-12-18 06:02:47.600243+00	41	t	Switzerland	4	Switzerland	Svizzera
2021-12-18 06:02:47.604309+00	42	t	Turkey	1	Turkey	Turchia
2021-12-18 06:02:47.608218+00	43	t	Canada	2	Canada	Canada
2021-12-18 06:02:47.612616+00	44	t	United States	2	United States	Stati Uniti
2021-12-18 06:02:47.616514+00	45	t	Mexico	2	Mexico	Messico
2021-12-18 06:02:47.620317+00	46	t	South Africa	3	South Africa	Sud Africa
2021-12-18 06:02:47.624342+00	47	t	Algeria	3	Algeria	Algeria
2021-12-18 06:02:47.628262+00	48	t	Bengladesh	1	Bengladesh	Bengladesh
2021-12-18 06:02:47.632173+00	49	t	Cambodia	1	Cambodia	Cambogia
2021-12-18 06:02:47.636216+00	50	t	China	1	China	Cina
2021-12-18 06:02:47.640105+00	51	t	South Korea	1	South Korea	Corea del Sud
2021-12-18 06:02:47.64383+00	52	t	Egypt	3	Egypt	Egitto
2021-12-18 06:02:47.64781+00	53	t	United Arab Emirates	3	United Arab Emirates	Emirati Arabi Uniti
2021-12-18 06:02:47.652435+00	54	t	India	1	India	India
2022-02-10 09:12:40.495536+00	55	t	Australia	5	Australia	Australia
\.


--
-- Data for Name: search_importquery; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.import_query (created_at, id, is_active, text, priority, priority_score, products_clicks, brand_id) FROM stdin;
2021-12-18 06:13:57.495377+00	33	t	Eachine	1	1.43	43	\N
2022-03-31 11:37:13.543501+00	15	t	iFlight	1	3.22	222	2
2021-12-18 06:12:19.941939+00	28	t	GPS	0	1.53	153	\N
2022-08-29 12:38:04.483864+00	42	t	Avatar	1	1.23	23	\N
2021-12-18 06:14:20.330848+00	35	t	ImpulseRC	1	1.35	35	\N
2021-12-18 06:05:03.058529+00	1	t	Motor	0	2.63	263	\N
2021-12-18 06:09:40.999103+00	22	t	HD	0	2.24	224	\N
2022-03-26 12:00:11.362922+00	38	t	Frame	1	1.95	95	\N
2022-05-05 06:58:30.212259+00	40	t	ORQA	1	1.05	5	\N
2021-12-18 06:05:13.936588+00	3	t	Goggles	0	2.51	251	\N
2021-12-18 06:13:37.091288+00	31	t	Zeez	1	1.19	19	\N
2022-11-21 11:49:33.215633+00	43	t	ELRS	1	1.19	19	\N
2021-12-18 06:09:53.377593+00	19	t	6S	0	2.9	290	\N
2021-12-18 06:11:12.964752+00	25	t	GEPRC	1	1.6099999999999999	61	\N
2022-03-31 11:41:32.73863+00	11	t	Caddx	1	2.84	184	4
2021-12-18 06:05:31.93426+00	5	t	Battery	0	3.21	321	\N
2021-12-18 06:06:06.696961+00	7	t	EMAX	1	1.81	81	\N
2021-12-18 06:15:14.531591+00	36	t	CNHL	1	1.11	11	\N
2021-12-18 06:11:00.146423+00	24	t	Flywoo	1	1.33	33	\N
2022-03-31 11:41:22.733933+00	18	t	Frsky	1	2.88	188	3
2021-12-18 06:05:20.322532+00	4	t	Radio	0	3.63	363	\N
2022-03-31 11:33:02.166391+00	10	t	TBS	1	3.36	236	1
2021-12-18 06:09:59.25874+00	21	t	Analog	0	2.06	206	\N
2021-12-18 06:08:02.372764+00	16	t	Ethix	1	1.55	55	\N
2022-05-05 06:57:58.974566+00	39	t	HDZero	1	1.11	11	\N
2021-12-18 06:13:00.538321+00	29	t	HGLRC	1	1.25	25	\N
2021-12-18 06:09:47.064294+00	20	t	4S	0	2.68	268	\N
2021-12-18 06:15:47.636572+00	37	t	Jumper	1	1.35	35	\N
2021-12-18 06:07:06.758296+00	12	t	Foxeer	1	1.6099999999999999	61	\N
2021-12-18 06:08:28.444015+00	17	t	Tattu	1	1.27	27	\N
2021-12-18 06:06:14.985547+00	8	t	T-Motor	1	2.4699999999999998	147	\N
2022-08-28 17:27:28.1673+00	41	t	Walksnail	1	1.11	11	\N
2021-12-18 06:11:29.592575+00	26	t	ISDT	1	1.43	43	\N
2021-12-18 06:07:14.532932+00	13	t	Runcam	1	1.77	77	\N
2021-12-18 06:10:19.232839+00	23	t	Frame	0	1.95	195	\N
2022-03-31 11:41:50.251399+00	9	t	Betafpv	1	1.8	80	5
2021-12-18 06:05:41.919108+00	6	t	Fatshark	1	1.31	31	\N
2021-12-18 06:07:27.952142+00	14	t	Lumenier	1	1.31	31	\N
2021-12-18 06:13:46.616157+00	32	t	Mamba	1	1.83	83	\N
2021-12-18 06:11:44.268764+00	27	t	Holybro	1	1.43	43	\N
2021-12-18 06:14:10.648933+00	34	t	ToolkitRC	1	1.07	7	\N
2021-12-18 06:05:07.749118+00	2	t	ESC	0	2.71	271	\N
2021-12-18 06:13:22.839164+00	30	t	RushFPV	1	1.19	19	\N
\.


--
-- Data for Name: search_store; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.store (created_at, id, is_active, name, website, last_check, is_parsable, search_url, search_tag, search_class, search_link, search_next_page, product_name_class, product_name_tag, product_price_class, product_price_tag, product_image_class, product_image_tag, product_thumb_class, product_thumb_tag, reason_could_not_be_parsed, currency, locale, product_is_available_class, product_is_available_tag, product_is_available_match, product_variations_class, product_variations_tag, scrape_with_js, product_description_class, product_description_tag, country_id, affiliate_id, affiliate_query_param, product_description_css_is_class, product_image_css_is_class, product_is_available_css_is_class, product_name_css_is_class, product_price_css_is_class, product_thumb_css_is_class, product_variations_css_is_class, search_page_param, logo) FROM stdin;
2022-02-25 13:44:28.561503+00	17	t	FPV24	https://www.fpv24.com	2023-04-21 04:55:48.200059+00	t	https://www.fpv24.com/en/search?search=	div	col-lg-3 col-md-4 col-6	boxed	\N	order-2	div	current	li	item	div				EUR	it_IT	green	div	(Ready for dispatch)	\N	\N	f	description	div	4	U-bHC329	aid	t	t	t	t	t	t	t	\N	\N
2022-03-24 08:22:42.297567+00	20	t	Drone Authority	https://www.droneauthority.co.uk	2023-04-21 05:01:46.286453+00	t	https://www.droneauthority.co.uk/search?type=product&q=	div	product-item	product-item__title	\N	product-meta__title	h1	price	span	product-gallery__image	img	\N	\N		GBP	en_US	product-form__inventory	span	(In stock)	\N	\N	f	card__section	div	10	o0b05i5o1g	ref	t	t	t	t	t	t	t	page	\N
2021-12-18 06:03:42.276962+00	5	t	B2B Drone	https://www.b2bonline.it/	2023-04-21 05:11:27.084814+00	t	http://b2bonline.it/it/index.php?fc=module&module=leoproductsearch&controller=productsearch&search_query=	div	ajax_block_product	product-title		product-detail-name	h1	current-price	div	js-qv-product-cover	img				EUR	it_IT	product-availability	span	(DISPONIBILITA'' IMMEDIATA)			f			1	\N	\N	t	t	t	t	t	t	t	\N	\N
2021-12-18 06:03:42.313415+00	10	t	GetFPV	https://www.getfpv.com/	2022-05-17 01:47:25.540952+00	t	https://www.getfpv.com/catalogsearch/result/?q=	li	item	product-name	next	product-name	div	price	span	gallery-image	img				USD	en_US	div_availability	div	In Stock	product-options	div	f	std	div	44	\N	\N	t	t	t	t	t	t	t	\N	\N
2022-02-18 08:09:38.274391+00	13	t	BuzzFPV	https://buzzfpv.com.au/	2023-04-21 16:02:33.436707+00	t	https://buzzfpv.com.au/index.php?route=product/search&limit=100&search=	div	product-layout	name	\N	page-title	h1	product-price	div	swiper-slide	div				AUD	en_US	product-stock	li	Stock: In stock	product-options	div	f	block-content	div	55	\N	\N	t	t	t	t	t	t	t	\N	\N
2021-12-28 20:54:49.151045+00	15	t	n-Factory.de	https://n-factory.de/	2023-04-21 02:25:05.984747+00	t	https://n-factory.de/navi.php?Sortierung=100&lang=eng&suche=	div	product-wrapper	title		product-title	h1	font-price	span	s360-product-gallery-image	div				EUR	it_IT	status	span	Available now!			f	desc	div	4			t	t	t	t	t	t	t	\N	\N
2022-03-13 16:49:23.654262+00	18	t	Pyro Drone	https://pyrodrone.com/	2022-05-06 12:30:58.809592+00	t	https://pyrodrone.com/pages/search-results-page?q=	li	snize-product	snize-view-link		product-single__title	h1	ProductPrice-product-template	span	product-featured-img	img				USD	en_US	AddToCartText-product-template	span	(Add to cart)	product-form__variants	select	t	product-description	div	44			t	t	f	t	f	t	t		\N
2021-12-26 18:35:20.33269+00	7	t	Drone24Hours	https://www.drone24hours.com/	2023-04-21 04:29:47.074326+00	t	https://www.drone24hours.com/?post_type=product&type_aws=true&s=	div	product-inner	woo-loop-product__title	next	product_title	h1	woocommerce-Price-amount	span	wp-post-image	img				EUR	en_US	stock	p	(\\d+ disponibili)	variations	table	f	woocommerce-Tabs-panel--description	div	1	lucapalonca	D24H	t	t	t	t	t	t	t	\N	\N
2022-09-13 11:50:09.292488+00	9	t	Drone FPV Racer	https://www.drone-fpv-racer.com/	2023-04-21 03:06:57.978348+00	t	https://www.drone-fpv-racer.com/en/recherche?controller=search&s=	article	col-xl-2	d-block	next	product-title	h1	current-price	div	js-qv-product-cover	img				EUR	en_US	product-availability	span	Same day shipping	\N	\N	f	product-caracteristiques	div	2	75	aff	t	t	f	t	t	t	t	\N	
2022-04-04 09:24:53.745063+00	2	t	FarinFrames	https://www.farinsframes.com/	2023-04-21 04:39:41.656372+00	t	https://www.farinsframes.com/search.php?search_query=	li	product	card-title	pagination-item--next	productView-title	h1	price--withoutTax	span	productView-img-container	div				EUR	en_US	productView-info	dl	(Disponibile|New)	form-option-wrapper	div	f	\N	\N	1	\N	\N	t	t	t	t	t	t	t	\N	
2021-12-27 21:48:27.170473+00	14	t	HobbyRC UK	https://www.hobbyrc.co.uk/	2023-04-21 04:46:40.26594+00	t	https://www.hobbyrc.co.uk/search?q=	div	item-box	product-title	next-page	product-name	div	product-price	div	picture	div				GBP	en_US	value	span	In stock	\N	\N	f	full-description	div	10	\N	\N	t	t	t	t	t	t	t	\N	\N
2023-04-19 08:12:35.323847+00	1	t	RHobbyFPV	https://www.rhobbyfpv.it/	2023-04-19 08:12:35.323621+00	t	https://www.rhobbyfpv.it/?post_type=product&s=	li	jet-woo-builder-product	jet-woo-builder-archive-product-title	\N	product_title	h1	woocommerce-Price-amount	span	wp-post-image	img				EUR	it_IT	stock	p	(\\d+ disponibili)	variations	table	f	\N	\N	1	iamlucafpv	ref	t	t	t	t	t	t	t	\N	
2021-12-28 20:23:43.747309+00	12	t	RaceDayQuads	https://www.racedayquads.com/	2023-04-21 09:20:37.180455+00	t	https://racedayquads.com/search?type=product&q=	article	productgrid--item	productitem--title	pagination--next	product-title	h1	price--main	div	pixelzoom--image	img				USD	en_US	in-stock	div	In Stock	form-options-container	div	f	ui-widget-content	div	44	\N	\N	t	t	t	t	t	t	t	\N	\N
2022-04-13 15:54:07.021443+00	19	t	NewBeeDrone	https://newbeedrone.com	2023-04-21 09:23:09.311258+00	t	https://newbeedrone.com/search?q=	div	boost-pfs-filter-product-item-inner	boost-pfs-filter-product-item-title	\N	product-title	div	ProductPrice-product-template	span	ProductImage-product-template	img	\N	\N		USD	en_US	AddToCartText-product-template	span	(Add to Cart)	\N	\N	f	description	dd	44	\N	\N	t	f	f	t	f	t	t	page	
2022-02-10 15:45:44.521036+00	16	t	FPV Faster	https://www.fpvfaster.com.au/	2023-04-21 15:20:00.234038+00	t	https://www.fpvfaster.com.au/search?type=product&q=	div	search-result	product-grid-item	\N	h2	h1	money	span	photo-	img	\N	\N		AUD	en_US	addToCartText	span	Add to Cart	selector-wrapper	div	f	description	div	55	\N	\N	t	t	t	t	t	t	t	page	\N
2022-02-10 14:51:22.671043+00	11	t	Rotor Riot	https://rotorriot.com/	2022-04-27 09:21:49.788054+00	t	https://rotorriot.com/search?type=product&q=	div	product-item	product-item__title	pagination__next	product-meta__title	h1	price	span	product-gallery__image	img				USD	en_US	product-form__inventory	span	(Low stock - order soon!|In stock)	product-form__option	div	f	text--pull	div	44	\N	\N	t	t	t	t	t	t	t	\N	\N
2022-03-25 08:20:34.464107+00	4	t	PersonalDrones	https://www.personaldrones.it/	2022-03-25 08:20:34.463721+00	f	https://www.personaldrones.it/ricerca?controller=search&orderby=position&orderway=desc&search_category=all&s=	div	item-inner	productName	next	h1	h1	current-price	div	js-qv-product-cover	img			The search for Motor did not produced any url	EUR	it_IT	product-add-to-cart	div	\\w*\\s*Pronta consegna|Ultimi articoli in magazzino			t			1	\N	\N	t	t	t	t	t	t	t	\N	\N
2021-12-18 06:03:42.283877+00	6	t	CostruzioneDroni	https://www.costruzionedroni.it/	2023-04-21 03:31:36.122027+00	t	https://www.costruzionedroni.it/ricerca?controller=search&s=	div	product_list_item	pro_first_box		product_name	h1	current-price	div	pro_gallery_item	img				EUR	it_IT	product-available	div	Disponibile			f			1	\N	\N	t	t	t	t	t	t	t	\N	\N
2022-03-24 16:48:43.842467+00	22	t	Rotor Village	https://rotorvillage.ca	2023-04-21 09:31:35.870354+00	t	https://rotorvillage.ca/search.php?section=product&search_query=	article	card	card-body	\N	productView-title	h1	price--withoutTax	span	productView-image--default	img	\N	\N		CAD	en_US	form-field--increments	div	Quantity:	\N	\N	f	tab-description	div	43	\N	\N	f	t	t	t	t	t	t	\N	\N
2022-04-07 07:48:56.633184+00	23	t	MantisFPV	https://www.mantisfpv.com.au	2023-04-21 16:37:58.467249+00	t	https://www.mantisfpv.com.au/?post_type=product&dgwt_wcas=1&s=	li	type-product	woocommerce-loop-product__link	\N	et_pb_wc_title	div	woocommerce-Price-amount	span	zoomImg	img	\N	\N		AUD	en_US	stock	p	(In stock)	\N	\N	f	et_pb_wc_description	div	55	\N	\N	t	t	t	t	t	t	t	\N	uploads/MantisFPV-logo.jpg
2022-03-24 10:02:44.155505+00	21	t	Unmanned Tech UK	https://www.unmannedtechshop.co.uk/	2023-04-17 13:47:43.088322+00	t	https://www.unmannedtechshop.co.uk/search-results/?q=	li	snize-product	snize-view-link	\N	product-title	h1	woocommerce-Price-amount	span	skip-lazy	img	\N	\N		GBP	en_US	stock	p	(In stock|Only \\d+ left in stock)	variations	table	t	woocommerce-Tabs-panel--description	div	10	\N	\N	t	t	t	t	t	t	t	\N	\N
2021-12-18 06:03:42.298112+00	8	t	HGLRC	https://www.hglrc.com/	2023-04-20 18:22:47.431716+00	t	https://www.hglrc.com/search?type=product&options%5Bunavailable_products%5D=last&options%5Bprefix%5D=last&q=	div	product-inner	cd	next	product_title	h1	money	span	op_0	img				USD	en_US				swatch	div	f	sp-tab-content	div	50	\N	\N	t	t	t	t	t	t	t	\N	\N
2021-12-18 06:03:42.262942+00	3	t	BetaFPV	https://betafpv.com/	2023-04-20 18:22:47.511495+00	t	https://betafpv.com/search?type=product%2Carticle%2Cpage&q=	div	grid-product	grid-product__link	next	product-single__title	h1	money	span	lazyloaded	img				USD	en_US				variant-wrapper	div	f	product-single__description	div	50	\N	\N	t	t	t	t	t	t	t	\N	\N
\.


--
-- Data for Name: search_shippingzone; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipping_zone (created_at, id, is_active, name) FROM stdin;
2021-12-18 06:03:23.120054+00	1	t	DroneFPVRacer - DHL Express - Zone 1
2021-12-18 06:03:23.123047+00	2	t	DroneFPVRacer - DHL Express - Zone 2
2021-12-18 06:03:23.124563+00	3	t	DroneFPVRacer - DHL Express - Zone 3
2021-12-18 06:03:23.125962+00	4	t	DroneFPVRacer - DHL Express - Zone 4
2021-12-18 06:03:23.12736+00	5	t	DroneFPVRacer - DHL Express - Zone 5
2021-12-18 06:03:23.128553+00	6	t	DroneFPVRacer - DHL Express - Zone 6
2021-12-18 06:03:23.129769+00	7	t	USA
2021-12-28 20:54:24.568496+00	8	t	n-Factory - Germany
2021-12-28 20:54:24.602757+00	9	t	n-Factory - Europe
2022-02-10 09:12:55.695582+00	10	t	Australia
2022-02-18 19:48:24.319145+00	11	t	FPV24 - Germania
2022-02-18 19:48:39.062251+00	12	t	FPV24 - Austria
2022-02-18 19:49:04.195361+00	13	t	FPV24 - Europe 0
2022-02-18 19:51:35.090458+00	14	t	FPV24 - Europe Zone 1
2022-02-18 19:54:01.691725+00	15	t	FPV24 - Europe Zone 2
2022-02-18 19:54:38.595788+00	16	t	FPV24 - Europe Zone 3
2022-02-18 19:55:03.224293+00	17	t	FPV24 - International
\.


--
-- Data for Name: search_shippingmethod; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipping_method (created_at, id, is_active, name, min_shipping_time, max_shipping_time, price, store_id, name_en, name_it, min_price_shipping_condition, is_vat_included, shipping_zone_id, currency, is_weight_dependent) FROM stdin;
2021-12-19 17:38:46.361646+00	43	t	Standard Shipping	2	5	8.00	6	Standard Shipping	Spedizione Standard	\N	t	\N	EUR	f
2021-12-19 17:38:46.368596+00	44	t	Express Shipping	1	2	9.90	6	Express Shipping	Spedizione Express	\N	t	\N	EUR	f
2021-12-19 17:38:46.374928+00	45	t	Standard Shipping	1	2	6.90	4	Standard Shipping	Spedizione Standard	\N	t	\N	EUR	f
2021-12-19 17:38:46.381142+00	46	t	Free Shipping	1	\N	\N	1	Free Shipping	Spedizione Gratuita	199.00	t	\N	EUR	f
2021-12-19 17:38:46.386874+00	47	t	Free Shipping	1	2	\N	4	Free Shipping	Spedizione Gratuita	100.00	t	\N	EUR	f
2021-12-19 17:38:46.393245+00	48	t	Free Shipping	1	2	\N	10	Free Shipping	Spedizione Gratuita	80.00	t	7	USD	f
2021-12-19 17:38:46.399085+00	49	t	Free Shipping	1	\N	\N	6	Free Shipping	Spedizione Gratuita	199.00	t	\N	EUR	f
2021-12-19 17:38:46.404416+00	50	t	Free Shipping	1	\N	\N	7	Free Shipping	Spedizione Gratuita	149.00	t	\N	EUR	f
2021-12-19 17:38:46.410197+00	51	t	Free Shipping	1	\N	\N	2	Free Shipping	Spedizione Gratuita	200.00	t	\N	EUR	f
2021-12-19 17:38:46.415527+00	52	t	DHL Express - Zone 1	1	\N	10.60	9	DHL Express - Zone 1	DHL Express - Zona 1	\N	f	1	EUR	f
2021-12-19 17:38:46.42071+00	53	t	DHL Express - Zone 1	1	\N	5.60	9	DHL Express - Zone 1	DHL Express - Zona 1	79.00	f	1	EUR	f
2021-12-19 17:38:46.426001+00	54	t	DHL Express - Zone 2	1	\N	11.18	9	DHL Express - Zone 2	DHL Express - Zona 2	\N	f	2	EUR	f
2021-12-19 17:38:46.43218+00	55	t	DHL Express - Zone 2	1	\N	6.18	9	DHL Express - Zone 2	DHL Express - Zona 2	79.00	f	2	EUR	f
2021-12-19 17:38:46.438071+00	56	t	DHL Express - Zone 3	1	\N	6.54	9	DHL Express - Zone 3	DHL Express - Zona 3	79.00	f	3	EUR	f
2021-12-19 17:38:46.444397+00	57	t	Free Shipping - Zone 3	1	\N	\N	9	Free Shipping - Zone 3	Spedizione Gratuita - Zona 3	200.00	f	3	EUR	f
2021-12-19 17:38:46.45015+00	58	t	Free Shipping - Zone 2	1	\N	\N	9	Free Shipping - Zone 2	Spedizione Gratuita - Zona 2	200.00	f	2	EUR	f
2021-12-19 17:38:46.456343+00	59	t	Free Shipping - Zone 1	1	\N	\N	9	Free Shipping - Zone 1	Spedizione Gratuita - Zona 1	200.00	f	1	EUR	f
2021-12-19 17:38:46.462711+00	60	t	DHL Express	1	\N	9.99	7	DHL Express	DHL Express	\N	t	\N	EUR	f
2021-12-19 17:38:46.469289+00	61	t	DHL Express	1	\N	9.90	2	DHL Express	DHL Express	\N	t	\N	EUR	f
2021-12-19 17:38:46.476396+00	62	t	DHL Express	1	\N	4.90	2	DHL Express	DHL Express	49.00	t	\N	EUR	f
2021-12-19 17:38:46.484245+00	63	t	SDA/DHL Express	1	2	10.00	1	SDA/DHL Express	SDA/DHL Express	\N	t	\N	EUR	f
2021-12-19 17:38:46.490757+00	64	t	DHL Express - Zone 3	1	\N	11.54	9	DHL Express - Zone 3	DHL Express - Zona 3	\N	f	3	EUR	f
2021-12-19 17:38:46.497096+00	65	t	DHL Express - Zone 4	2	\N	16.94	9	DHL Express - Zone 4	DHL Express - Zona 4	\N	f	4	EUR	f
2021-12-19 17:38:46.504157+00	66	t	DHL Express - Zone 4	2	\N	11.94	9	DHL Express - Zone 4	DHL Express - Zona 4	79.00	f	4	EUR	f
2021-12-19 17:38:46.512024+00	67	t	DHL Express - Zone 4	2	\N	6.94	9	DHL Express - Zone 4	DHL Express - Zona 4	200.00	f	4	EUR	f
2021-12-19 17:38:46.519771+00	68	t	DHL Worldwide	2	3	36.43	10	DHL Worldwide	DHL Internazionale	\N	t	\N	USD	f
2021-12-19 17:38:46.527579+00	69	t	Standard Shipping	12	30	10.00	3	Standard Shipping	Spedizione Standard	\N	t	\N	USD	f
2021-12-19 17:38:46.534825+00	70	t	Standard Shipping	12	30	5.00	3	Standard Shipping	Spedizione Standard	20.00	t	\N	USD	f
2021-12-19 17:38:46.541815+00	71	t	Economy Shipping Worldwide	7	30	18.00	10	Economy Shipping Worldwide	Spedizione economica internazionale	\N	t	\N	USD	f
2021-12-19 17:38:46.549155+00	72	t	Expedited Shipping	3	7	25.00	3	Expedited Shipping	Spedizione Veloce	\N	t	\N	USD	f
2021-12-19 17:38:46.556483+00	73	t	DHL Express	3	8	29.95	8	DHL Express	DHL Express	\N	t	\N	USD	f
2021-12-19 17:38:46.563716+00	74	t	Free Shipping	3	8	\N	8	Free Shipping	Spedizione Gratuita	119.00	t	\N	USD	f
2021-12-19 17:38:46.570831+00	75	t	Free Shipping	12	30	\N	3	Free Shipping	Spedizione Gratuita	99.00	t	\N	USD	f
2021-12-19 17:38:46.577841+00	76	t	Free Shipping - Zone 4	2	\N	\N	9	Free Shipping - Zone 4	Spedizione Gratuita - Zona 4	300.00	f	4	EUR	f
2021-12-19 17:38:46.585004+00	77	t	Free Shipping	1	\N	\N	11	Free Shipping	Spedizione Gratuita	50.00	t	7	USD	f
2021-12-19 17:38:46.592413+00	78	t	USPS Worldwide	6	30	20.07	11	USPS Worldwide	USPS Internazionale	\N	t	\N	USD	f
2021-12-19 17:38:46.599241+00	79	t	DHL Worldwide	3	8	31.75	11	DHL Worldwide	DHL Internazionale	\N	t	\N	USD	f
2021-12-28 20:55:04.529011+00	80	t	DHL worldwide	7	10	29.00	15	DHL worldwide	DHL Internazionale	\N	t	\N	EUR	f
2021-12-28 20:55:04.538413+00	81	t	Worldwide delivery	7	10	4.95	15	Worldwide delivery	Consegna internazionale	\N	t	\N	EUR	f
2021-12-28 20:55:04.543459+00	82	t	Free shipping - Europe	1	\N	\N	15	Free shipping - Europe	Spedizione gratuita - Europa	200.00	t	\N	EUR	f
2021-12-28 20:55:04.548076+00	83	t	Free Shipping - Germany	1	\N	\N	15	Free Shipping - Germany	Spedizione gratuita - Germania	100.00	t	8	EUR	f
2021-12-28 20:55:04.553624+00	84	t	Registered Air Mail - Europe	1	\N	6.95	15	Registered Air Mail - Europe	Posta - Europa	\N	t	9	EUR	f
2021-12-28 20:55:04.559043+00	85	t	DHL Express - Europe	1	\N	15.00	15	DHL Express - Europe	DHL Express - Europa	\N	t	9	EUR	f
2021-12-28 20:55:04.563991+00	86	t	DHL Express - Germany	1	\N	11.90	15	DHL Express - Germany	DHL Express - Germania	\N	t	8	EUR	f
2021-12-28 20:55:04.569124+00	87	t	DHL Package - Germany	2	\N	3.90	15	DHL Package - Germany	Pacchetto DHL - Germania	\N	t	8	EUR	f
2022-02-18 08:07:16.688946+00	88	t	Standard Shipping	1	6	\N	16	Standard Shipping	Spedizione Standard	\N	t	10	AUD	t
2022-02-18 08:08:08.993654+00	89	t	Free Shipping	1	6	\N	16	Free Shipping	Spedizione Gratuita	99.00	t	10	AUD	f
2022-02-18 08:08:56.948812+00	90	t	Express Free Shipping	1	\N	\N	16	Express Free Shipping	Spedizione Gratuita Veloce	250.00	t	10	AUD	f
2022-03-13 16:57:02.222877+00	91	t	Free Shipping	1	\N	\N	18	Free Shipping	Spedizione gratuita	60.00	t	7	USD	f
2022-03-13 17:01:52.288766+00	92	t	Stardard Shipping	1	\N	4.90	18	Stardard Shipping	Spedizione Standard	\N	t	7	USD	f
2022-03-26 12:03:08.97988+00	93	t	Free Shipping	1	\N	\N	12	Free Shipping	Spedizione Gratuita	60.00	t	7	USD	f
2022-03-26 12:05:09.464932+00	94	t	International Shipping	1	\N	\N	12	International Shipping	Spedizione Internazionale	\N	t	\N	USD	t
\.


--
-- Data for Name: search_shipping_zone_ship_to; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shipping_zone_country_link (shipping_zone_id, country_id) FROM stdin;
8	4
9	1
9	2
9	3
9	5
9	7
9	8
9	9
9	10
9	11
9	12
9	13
9	14
9	15
9	16
9	17
9	19
9	20
9	21
9	22
9	23
9	24
9	26
10	55
11	4
12	11
13	8
13	3
14	1
14	2
14	5
14	6
14	7
14	9
14	10
14	12
14	13
14	14
14	15
14	16
14	17
14	18
14	20
14	22
15	32
15	34
15	36
15	38
15	39
15	40
15	28
15	31
16	41
16	35
17	42
17	43
17	44
\.


--
-- Name: search_brand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.brand_id_seq', 5, true);


--
-- Name: search_clickedproduct_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.clicked_product_id_seq', 2429, true);


--
-- Name: search_continent_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.continent_id_seq', 5, true);


--
-- Name: search_country_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.country_id_seq', 55, true);


--
-- Name: search_importquery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.import_query_id_seq', 43, true);



--
-- Name: search_shippingmethod_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shipping_method_id_seq', 94, true);


--
-- Name: search_shippingzone_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shipping_zone_id_seq', 17, true);

--
-- Name: search_store_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.store_id_seq', 23, true);


--
-- PostgreSQL database dump complete
--

