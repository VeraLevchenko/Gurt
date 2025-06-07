--
-- PostgreSQL database dump
--

-- Dumped from database version 12.22 (Ubuntu 12.22-0ubuntu0.20.04.4)
-- Dumped by pg_dump version 12.22 (Ubuntu 12.22-0ubuntu0.20.04.4)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO vera;

--
-- Name: contract_additional_files; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.contract_additional_files (
    contract_id integer NOT NULL,
    file_path character varying(255) NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.contract_additional_files OWNER TO vera;

--
-- Name: contract_documents; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.contract_documents (
    contract_id integer NOT NULL,
    file_path character varying(255) NOT NULL
);


ALTER TABLE public.contract_documents OWNER TO vera;

--
-- Name: contract_work_types; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.contract_work_types (
    contract_id integer NOT NULL,
    work_type_id integer NOT NULL
);


ALTER TABLE public.contract_work_types OWNER TO vera;

--
-- Name: contracts; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.contracts (
    id integer NOT NULL,
    number character varying(50) NOT NULL,
    contract_date date NOT NULL,
    price double precision NOT NULL,
    address character varying(255) NOT NULL,
    physical_person_id integer,
    legal_entity_id integer,
    object_name character varying(255) NOT NULL
);


ALTER TABLE public.contracts OWNER TO vera;

--
-- Name: contracts_id_seq; Type: SEQUENCE; Schema: public; Owner: vera
--

CREATE SEQUENCE public.contracts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contracts_id_seq OWNER TO vera;

--
-- Name: contracts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vera
--

ALTER SEQUENCE public.contracts_id_seq OWNED BY public.contracts.id;


--
-- Name: legal_entities; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.legal_entities (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    inn character varying(50) NOT NULL,
    legal_address character varying(255) NOT NULL,
    director_full_name character varying(255) NOT NULL,
    payment_details text NOT NULL,
    phone character varying(50) NOT NULL,
    email character varying(255)
);


ALTER TABLE public.legal_entities OWNER TO vera;

--
-- Name: legal_entities_id_seq; Type: SEQUENCE; Schema: public; Owner: vera
--

CREATE SEQUENCE public.legal_entities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.legal_entities_id_seq OWNER TO vera;

--
-- Name: legal_entities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vera
--

ALTER SEQUENCE public.legal_entities_id_seq OWNED BY public.legal_entities.id;


--
-- Name: physical_persons; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.physical_persons (
    id integer NOT NULL,
    full_name character varying(255) NOT NULL,
    passport character varying(255) NOT NULL,
    address character varying(255) NOT NULL,
    phone character varying(50) NOT NULL,
    email character varying(50)
);


ALTER TABLE public.physical_persons OWNER TO vera;

--
-- Name: physical_persons_id_seq; Type: SEQUENCE; Schema: public; Owner: vera
--

CREATE SEQUENCE public.physical_persons_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.physical_persons_id_seq OWNER TO vera;

--
-- Name: physical_persons_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vera
--

ALTER SEQUENCE public.physical_persons_id_seq OWNED BY public.physical_persons.id;


--
-- Name: work_types; Type: TABLE; Schema: public; Owner: vera
--

CREATE TABLE public.work_types (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    price double precision NOT NULL,
    unit character varying(50) NOT NULL,
    price_with_vat double precision NOT NULL
);


ALTER TABLE public.work_types OWNER TO vera;

--
-- Name: work_types_id_seq; Type: SEQUENCE; Schema: public; Owner: vera
--

CREATE SEQUENCE public.work_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.work_types_id_seq OWNER TO vera;

--
-- Name: work_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vera
--

ALTER SEQUENCE public.work_types_id_seq OWNED BY public.work_types.id;


--
-- Name: contracts id; Type: DEFAULT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contracts ALTER COLUMN id SET DEFAULT nextval('public.contracts_id_seq'::regclass);


--
-- Name: legal_entities id; Type: DEFAULT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.legal_entities ALTER COLUMN id SET DEFAULT nextval('public.legal_entities_id_seq'::regclass);


--
-- Name: physical_persons id; Type: DEFAULT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.physical_persons ALTER COLUMN id SET DEFAULT nextval('public.physical_persons_id_seq'::regclass);


--
-- Name: work_types id; Type: DEFAULT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.work_types ALTER COLUMN id SET DEFAULT nextval('public.work_types_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.alembic_version (version_num) FROM stdin;
2b8b469977d0
\.


--
-- Data for Name: contract_additional_files; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.contract_additional_files (contract_id, file_path, id) FROM stdin;
\.


--
-- Data for Name: contract_documents; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.contract_documents (contract_id, file_path) FROM stdin;
\.


--
-- Data for Name: contract_work_types; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.contract_work_types (contract_id, work_type_id) FROM stdin;
\.


--
-- Data for Name: contracts; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.contracts (id, number, contract_date, price, address, physical_person_id, legal_entity_id, object_name) FROM stdin;
\.


--
-- Data for Name: legal_entities; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.legal_entities (id, name, inn, legal_address, director_full_name, payment_details, phone, email) FROM stdin;
1	ыва	ыва	ыва	ыва	ыва	741817	180982@mail.ru
3	1	1	1	1	1	741817	180982@mail.ru
12	bbbbbb	dfzh	dfh	zdfh	dzfh	741817	180982@mail.ru
\.


--
-- Data for Name: physical_persons; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.physical_persons (id, full_name, passport, address, phone, email) FROM stdin;
3	2	3	к23	741817	180982@mail.ru
4	4	4	4	741817	180982@mail.ru
5	5	ыв	ывм	741817	180982@mail.ru
7	7	7	7	741817	180982@mail.ru
10	1	уе	фпк	741817	180982@mail.ru
11	укпфукпфукп	фукпфукп	фукпфукп	741817	180982@mail.ru
14	77777	ваи	7г	3	180982@mail.ru
15	1111	1111	111	741817	180982@mail.ru
1	1	2	1	741817	180982@mail.ru
6	6	777	6	741817	180982@mail.ru
16	Иванов Иван Иванович	3209 771224 выдан tryertherberthertherth	г.Новокузнецк, ул.Кирова, 12-44	8-991-122-1452	ivanov@mail.ru
17	Петров Петр Сергеевич	3200 142452 выдан 28.01.2020 Отделением №1 в центральном районе ОУФМС России рпо Кемеровской области в гор. Новокузнецке	Новокузнецк, улица Кирова, 12-64	741817	180982@mail.ru
\.


--
-- Data for Name: work_types; Type: TABLE DATA; Schema: public; Owner: vera
--

COPY public.work_types (id, name, price, unit, price_with_vat) FROM stdin;
1	Кадастровая съемка объектов гаражного назначения	2582.91	штук	3099.49
2	Кадастровая съемка (для ведения садоводства, огородничества, индивидуального жилищного строительства)	3889.53	штук	4667.44
3	Топографическая съемка незастроенной территории	36453.45	1 га	43744.14
4	Топографическая съемка застроенной территории	51018.82	1 га	61222.58
5	Исполнительная съемка подземных (наземных) коммуникаций до 10 м (включительно)	4277.25	штук	5132.7
6	Исполнительная съемка подземных (наземных) коммуникаций от 10 м до 50 м (включительно)	7226.72	штук	8672.06
7	Исполнительная съемка подземных (наземных) коммуникаций от 50 м до 100 м (включительно)	13980.76	штук	16776.91
8	Исполнительная съемка подземных (наземных) коммуникаций от 100 м до 200 м (включительно)	23735.57	штук	28482.68
9	Исполнительная съемка подземных (наземных) коммуникаций от 200 м до 500 м (включительно)	37359.9	штук	44831.88
10	Исполнительная съемка подземных (наземных) коммуникаций от 500 м до 1000 м (включительно)	67833.98	штук	81400.77
11	Вынос в натуру осей сооружений и зданий	15077.28	1 ось	18092.74
12	Создание планово-высотного обоснования	12685.03	1 км	15222.04
13	Вынос в натуру одного межевого знака	1025.88	1 знак	1231.06
14	Подготовка расчета необходимой площади для формирования земельного участка, на котором находятся здания, сооружения	3380.91	штук	4057.09
15	Подготовка графического материала	1005.77	штук	1206.92
16	Координатная привязка геодезических реперов	7875.26	штук	9450.31
17	Плановая и высотная привязка точек	2028.05	1 точка	2433.66
18	Обследование земельного участка с составлением акта	1373.86	штук	1648.63
19	Консультирование по вопросам действующего законодательства	351.58	штук	421.9
20	Составление карты (плана) объектов землеустройства протяженностью от 500 м до 1 км (включительно)	13147.19	штук	15776.63
21	Составление карты (плана) объектов землеустройства площадью до 1000 кв. м (включительно)	10466.33	штук	12559.6
22	Копирование документов (печать) формата А4 - одна сторона	11.66	штук	13.99
23	Копирование документов (печать) формата А3 - одна сторона	23.32	штук	27.98
24	Копирование документов (печать) форматов А1, А2 - одна сторона	204.07	штук	244.88
25	Копирование документов (печать) формата А0	641.36	штук	769.63
26	Внесение изменений в схему садоводческого некоммерческого товарищества 1 - 2 участка	2504.78	штук	3005.74
27	Внесение изменений в схему садоводческого некоммерческого товарищества 3 - 8 участков	6362.24	штук	7634.69
28	Внесение изменений в схему садоводческого некоммерческого товарищества 9 - 15 участков	9580.67	штук	11496.8
29	Подготовка схемы расположения на кадастровом плане территории до 2000 кв. м (включительно)	2023.77	штук	2428.52
30	Подготовка схемы расположения на кадастровом плане территории от 2000 кв. м до 5000 кв. м (включительно)	2405.09	штук	2886.11
31	Подготовка схемы расположения на кадастровом плане территории от 5000 кв. м до 10000 кв. м (включительно)	3539.11	штук	4246.93
32	Подготовка схемы расположения на кадастровом плане территории от 10000 кв. м до 15000 кв. м (включительно)	5494.08	штук	6592.9
33	Подготовка схемы для разрешения размещения объекта на земельном участке до 2000 кв. м (включительно)	2087.32	штук	2504.78
34	Подготовка схемы для разрешения размещения объекта на земельном участке от 2000 кв. м до 5000 кв. м (включительно)	2325.78	штук	2790.94
35	Подготовка схемы для разрешения размещения объекта на земельном участке от 5000 кв. м до 10000 кв. м (включительно)	3480.81	штук	4176.97
36	Подготовка схемы для разрешения размещения объекта на земельном участке от 10000 кв. м до 15000 кв. м (включительно)	5504.58	штук	6605.5
37	Составление акта обследования здания, сооружения до 500 кв. м (включительно)	3388.88	штук	4066.66
38	Подготовка технического плана (индивидуальное жилищное строительство, садовый дом)	4007.69	штук	4809.23
39	Подготовка технического плана на сооружения, здания общественного назначения до 1000 кв. м (включительно)	8994.71	штук	10793.65
40	Подготовка технического плана на сооружения, здания общественного назначения от 1000 кв. м до 2000 кв. м (включительно)	13140	штук	15768
41	Разработка межевого плана (для ведения садоводства, огородничества, индивидуального жилищного строительства)	5331.29	штук	6397.55
42	Разработка межевого плана, 1 участок до 10000 кв. м (включительно), за исключением услуги, указанной в п. 41 настоящего приложения	16942.12	штук	20330.54
43	Разработка межевого плана, 1 участок свыше 10000 кв. м, за исключением услуги, указанной в п. 41 настоящего приложения	23914.78	штук	28697.74
44	Подготовка проекта межевания территории	22915.61	1 га	27498.73
45	Разработка технического плана жилого помещения	159.05	кв. м	190.86
46	Разработка технического плана нежилого помещения	217.63	кв. м	261.16
\.


--
-- Name: contracts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vera
--

SELECT pg_catalog.setval('public.contracts_id_seq', 51, true);


--
-- Name: legal_entities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vera
--

SELECT pg_catalog.setval('public.legal_entities_id_seq', 12, true);


--
-- Name: physical_persons_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vera
--

SELECT pg_catalog.setval('public.physical_persons_id_seq', 17, true);


--
-- Name: work_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vera
--

SELECT pg_catalog.setval('public.work_types_id_seq', 46, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: contract_additional_files contract_additional_files_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_additional_files
    ADD CONSTRAINT contract_additional_files_pkey PRIMARY KEY (contract_id);


--
-- Name: contract_documents contract_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_documents
    ADD CONSTRAINT contract_documents_pkey PRIMARY KEY (contract_id);


--
-- Name: contract_work_types contract_work_types_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_work_types
    ADD CONSTRAINT contract_work_types_pkey PRIMARY KEY (contract_id, work_type_id);


--
-- Name: contracts contracts_number_key; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_number_key UNIQUE (number);


--
-- Name: contracts contracts_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_pkey PRIMARY KEY (id);


--
-- Name: legal_entities legal_entities_inn_key; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.legal_entities
    ADD CONSTRAINT legal_entities_inn_key UNIQUE (inn);


--
-- Name: legal_entities legal_entities_name_key; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.legal_entities
    ADD CONSTRAINT legal_entities_name_key UNIQUE (name);


--
-- Name: legal_entities legal_entities_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.legal_entities
    ADD CONSTRAINT legal_entities_pkey PRIMARY KEY (id);


--
-- Name: physical_persons physical_persons_passport_key; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.physical_persons
    ADD CONSTRAINT physical_persons_passport_key UNIQUE (passport);


--
-- Name: physical_persons physical_persons_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.physical_persons
    ADD CONSTRAINT physical_persons_pkey PRIMARY KEY (id);


--
-- Name: work_types work_types_name_key; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.work_types
    ADD CONSTRAINT work_types_name_key UNIQUE (name);


--
-- Name: work_types work_types_pkey; Type: CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.work_types
    ADD CONSTRAINT work_types_pkey PRIMARY KEY (id);


--
-- Name: contract_additional_files contract_additional_files_contract_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_additional_files
    ADD CONSTRAINT contract_additional_files_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES public.contracts(id);


--
-- Name: contract_documents contract_documents_contract_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_documents
    ADD CONSTRAINT contract_documents_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES public.contracts(id);


--
-- Name: contract_work_types contract_work_types_contract_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_work_types
    ADD CONSTRAINT contract_work_types_contract_id_fkey FOREIGN KEY (contract_id) REFERENCES public.contracts(id);


--
-- Name: contract_work_types contract_work_types_work_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contract_work_types
    ADD CONSTRAINT contract_work_types_work_type_id_fkey FOREIGN KEY (work_type_id) REFERENCES public.work_types(id);


--
-- Name: contracts contracts_legal_entity_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_legal_entity_id_fkey FOREIGN KEY (legal_entity_id) REFERENCES public.legal_entities(id);


--
-- Name: contracts contracts_physical_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vera
--

ALTER TABLE ONLY public.contracts
    ADD CONSTRAINT contracts_physical_person_id_fkey FOREIGN KEY (physical_person_id) REFERENCES public.physical_persons(id);


--
-- PostgreSQL database dump complete
--

