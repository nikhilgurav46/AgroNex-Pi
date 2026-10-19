#!/usr/bin/env python3
"""
AgroNex-Pi: Plant Disease Knowledge Base (§5.5)

Maps disease class labels to common names, biological causes, visual symptoms,
and actionable agronomic treatments (cultural and chemical controls).
Enriched to support full PlantVillage taxonomy.
"""

DISEASE_KNOWLEDGE_BASE = {
    # ---------------- Tomato Classes ----------------
    "Tomato___healthy": {
        "plant": "Tomato",
        "disease": "Healthy",
        "common_name": "Tomato — Healthy Leaf",
        "is_healthy": True,
        "cause": "N/A (Plant is in optimal physiological vigor)",
        "symptoms": "Vibrant green uniform foliage, robust leaf turgidity, no visual lesions or chlorosis.",
        "treatment": "Maintain regular drip irrigation and balanced N-P-K nutrient schedule."
    },
    "Tomato_healthy": {
        "plant": "Tomato",
        "disease": "Healthy",
        "common_name": "Tomato — Healthy Leaf",
        "is_healthy": True,
        "cause": "N/A (Plant is in optimal physiological vigor)",
        "symptoms": "Vibrant green uniform foliage, robust leaf turgidity, no visual lesions or chlorosis.",
        "treatment": "Maintain regular drip irrigation and balanced N-P-K nutrient schedule."
    },
    "Tomato___Early_blight": {
        "plant": "Tomato",
        "disease": "Early Blight",
        "common_name": "Tomato — Early Blight (Alternaria solani)",
        "is_healthy": False,
        "cause": "Fungal pathogen Alternaria solani, favored by warm temperatures (24-29°C) and persistent foliage dampness.",
        "symptoms": "Concentric target-spot rings on mature lower leaves surrounded by distinctive yellow chlorotic halos.",
        "treatment": "Apply copper fungicide or Chlorothalonil; prune lower leaves touching soil; maintain drip irrigation."
    },
    "Tomato_Early_blight": {
        "plant": "Tomato",
        "disease": "Early Blight",
        "common_name": "Tomato — Early Blight (Alternaria solani)",
        "is_healthy": False,
        "cause": "Fungal pathogen Alternaria solani, favored by warm temperatures (24-29°C) and persistent foliage dampness.",
        "symptoms": "Concentric target-spot rings on mature lower leaves surrounded by distinctive yellow chlorotic halos.",
        "treatment": "Apply copper fungicide or Chlorothalonil; prune lower leaves touching soil; maintain drip irrigation."
    },
    "Tomato___Late_blight": {
        "plant": "Tomato",
        "disease": "Late Blight",
        "common_name": "Tomato — Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "cause": "Destructive oomycete pathogen Phytophthora infestans, spreading rapidly in cool, humid, wet weather.",
        "symptoms": "Large, dark water-soaked necrotic lesions on leaf margins with white fuzzy mycelium sporulation on leaf undersides.",
        "treatment": "Immediate application of Mancozeb or systemic Metalaxyl/Ridomil Gold; destroy infected foliage; enhance air circulation."
    },
    "Tomato_Late_blight": {
        "plant": "Tomato",
        "disease": "Late Blight",
        "common_name": "Tomato — Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "cause": "Destructive oomycete pathogen Phytophthora infestans, spreading rapidly in cool, humid, wet weather.",
        "symptoms": "Large, dark water-soaked necrotic lesions on leaf margins with white fuzzy mycelium sporulation on leaf undersides.",
        "treatment": "Immediate application of Mancozeb or systemic Metalaxyl/Ridomil Gold; destroy infected foliage; enhance air circulation."
    },
    "Tomato_Bacterial_spot": {
        "plant": "Tomato",
        "disease": "Bacterial Spot",
        "common_name": "Tomato — Bacterial Spot (Xanthomonas spp.)",
        "is_healthy": False,
        "cause": "Bacterium Xanthomonas campestris pv. vesicatoria, spread through splashing water and contaminated seeds.",
        "symptoms": "Small, dark, water-soaked circular spots that dry and turn necrotic with yellow borders.",
        "treatment": "Apply copper hydroxide mixed with Mancozeb; sanitize tools; avoid overhead sprinkler watering."
    },
    "Tomato_Leaf_Mold": {
        "plant": "Tomato",
        "disease": "Leaf Mold",
        "common_name": "Tomato — Leaf Mold (Passalora fulva)",
        "is_healthy": False,
        "cause": "Fungus Passalora fulva, thrives in high greenhouse relative humidity (>85%).",
        "symptoms": "Pale greenish-yellow spots on upper leaf surfaces and olive-green velvety patches on undersides.",
        "treatment": "Ventilate greenhouses to reduce humidity; remove affected foliage; spray protective bio-fungicide."
    },
    "Tomato_Septoria_leaf_spot": {
        "plant": "Tomato",
        "disease": "Septoria Leaf Spot",
        "common_name": "Tomato — Septoria Leaf Spot (Septoria lycopersici)",
        "is_healthy": False,
        "cause": "Fungal pathogen Septoria lycopersici, overwintering in solanaceous plant debris.",
        "symptoms": "Numerous small circular spots with grayish-white centers and dark brown margins.",
        "treatment": "Rotate crops every 2-3 years; apply chlorothalonil or copper spray; mulch around plant base."
    },
    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "plant": "Tomato",
        "disease": "Two-Spotted Spider Mite Infestation",
        "common_name": "Tomato — Spider Mite Infestation (Tetranychus urticae)",
        "is_healthy": False,
        "cause": "Microscopic arachnid pest Tetranychus urticae feeding on leaf sap during dry, dusty conditions.",
        "symptoms": "Fine yellow stippling/speckling across leaf blade, curling leaves, and fine silky webbing underneath.",
        "treatment": "Apply insecticidal soap, neem oil spray, or release predatory mites (Phytoseiulus persimilis)."
    },
    "Tomato__Target_Spot": {
        "plant": "Tomato",
        "disease": "Target Spot",
        "common_name": "Tomato — Target Spot (Corynespora cassiicola)",
        "is_healthy": False,
        "cause": "Fungal pathogen Corynespora cassiicola, prevalent in warm, humid tropical and subtropical climates.",
        "symptoms": "Brown circular lesions with light brown centers and dark concentric rings resembling targets.",
        "treatment": "Ensure row spacing for airflow; spray azoxystrobin or copper fungicides."
    },
    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "plant": "Tomato",
        "disease": "Yellow Leaf Curl Virus",
        "common_name": "Tomato — Yellow Leaf Curl Virus (TYLCV)",
        "is_healthy": False,
        "cause": "Begomovirus transmitted exclusively by the sweetpotato whitefly (Bemisia tabaci).",
        "symptoms": "Severe upward leaf cupping/curling, yellow chlorosis between veins, stunted plant growth, aborted flowers.",
        "treatment": "Control whitefly vectors using yellow sticky traps and imidacloprid; remove infected plants immediately."
    },
    "Tomato__Tomato_mosaic_virus": {
        "plant": "Tomato",
        "disease": "Tomato Mosaic Virus",
        "common_name": "Tomato — Mosaic Virus (ToMV)",
        "is_healthy": False,
        "cause": "Highly stable tobamovirus transmitted via mechanical contact, handling, and infected seed.",
        "symptoms": "Mottled light and dark green mosaic patterns on foliage, leaf distortion, 'shoestring' fern-like appearance.",
        "treatment": "Sanitize tools with 20% non-fat dry milk solution; plant certified virus-resistant cultivars; eradicate diseased specimens."
    },

    # ---------------- Potato Classes ----------------
    "Potato___healthy": {
        "plant": "Potato",
        "disease": "Healthy",
        "common_name": "Potato — Healthy Leaf",
        "is_healthy": True,
        "cause": "N/A (Plant is in optimal vigor)",
        "symptoms": "Uniform deep green leaf structure, crisp texture, no necrotic spots or wilt.",
        "treatment": "Continue standard field management, balanced nitrogen fertilization, and soil moisture monitoring."
    },
    "Potato___Early_blight": {
        "plant": "Potato",
        "disease": "Early Blight",
        "common_name": "Potato — Early Blight (Alternaria solani)",
        "is_healthy": False,
        "cause": "Fungal pathogen Alternaria solani, survives in decaying crop debris and volunteer potato tubers.",
        "symptoms": "Dark brown angular spots with characteristic concentric rings on mature lower foliage.",
        "treatment": "Spray preventative fungicides (e.g. Mancozeb, Azoxystrobin); rotate crops with non-solanaceous species."
    },
    "Potato___Late_blight": {
        "plant": "Potato",
        "disease": "Late Blight",
        "common_name": "Potato — Late Blight (Phytophthora infestans)",
        "is_healthy": False,
        "cause": "Oomycete pathogen Phytophthora infestans, highly destructive under cool damp field conditions.",
        "symptoms": "Irregular dark green to purplish-black water-soaked lesions rapidly expanding inward from leaf tips and margins.",
        "treatment": "Apply systemic fungicides (e.g., Metalaxyl, Cymoxanil); destroy infected tubers; maintain high soil ridges."
    },

    # ---------------- Pepper (Bell) Classes ----------------
    "Pepper__bell___healthy": {
        "plant": "Bell Pepper",
        "disease": "Healthy",
        "common_name": "Bell Pepper — Healthy Leaf",
        "is_healthy": True,
        "cause": "N/A (Plant is in optimal vigor)",
        "symptoms": "Smooth, glossy, deep-green foliage without spotting or curling.",
        "treatment": "Maintain regular watering and organic compost mulching."
    },
    "Pepper__bell___Bacterial_spot": {
        "plant": "Bell Pepper",
        "disease": "Bacterial Spot",
        "common_name": "Bell Pepper — Bacterial Spot (Xanthomonas euvesicatoria)",
        "is_healthy": False,
        "cause": "Bacterium Xanthomonas campestris pv. vesicatoria, enters through natural leaf stomata and wounds.",
        "symptoms": "Small, slightly raised blister-like spots that darken to brown/black with greasy water-soaked margins.",
        "treatment": "Apply copper bactericide combined with Mancozeb; sanitize seed stock; rotate with non-host crops."
    },

    # ---------------- Corn (Maize) Classes ----------------
    "Corn___healthy": {
        "plant": "Corn", "disease": "Healthy", "common_name": "Corn — Healthy Leaf",
        "is_healthy": True, "cause": "N/A (Plant is in optimal vigor)",
        "symptoms": "Uniform green blades, no pustules or lesions.",
        "treatment": "Maintain nitrogen schedule and adequate row spacing.",
    },
    "Corn___Common_rust": {
        "plant": "Corn", "disease": "Common Rust", "common_name": "Corn — Common Rust (Puccinia sorghi)",
        "is_healthy": False,
        "cause": "Windborne fungal spores of Puccinia sorghi, favored by cool moist conditions.",
        "symptoms": "Small reddish-brown pustules scattered on both leaf surfaces.",
        "treatment": "Plant rust-resistant hybrids; apply foliar fungicide if severe before tasseling.",
    },
    "Corn___Gray_leaf_spot": {
        "plant": "Corn", "disease": "Gray Leaf Spot", "common_name": "Corn — Gray Leaf Spot (Cercospora zeae-maydis)",
        "is_healthy": False,
        "cause": "Cercospora zeae-maydis, favored by high humidity and infected crop residue.",
        "symptoms": "Rectangular tan-to-gray lesions running parallel to leaf veins.",
        "treatment": "Rotate crops, manage residue, apply triazole or strobilurin fungicide.",
    },

    # ---------------- Grape Classes ----------------
    "Grape___healthy": {
        "plant": "Grape", "disease": "Healthy", "common_name": "Grape — Healthy Leaf",
        "is_healthy": True, "cause": "N/A (Plant is in optimal vigor)",
        "symptoms": "Firm green leaves without discoloration.",
        "treatment": "Standard canopy management and irrigation.",
    },
    "Grape___Black_rot": {
        "plant": "Grape", "disease": "Black Rot", "common_name": "Grape — Black Rot (Guignardia bidwellii)",
        "is_healthy": False,
        "cause": "Fungal pathogen Guignardia bidwellii, thrives in warm humid weather.",
        "symptoms": "Tan circular lesions with dark borders and black fruiting bodies.",
        "treatment": "Remove mummified berries, apply mancozeb from bud break, improve canopy airflow.",
    },
    "Grape___Leaf_blight": {
        "plant": "Grape", "disease": "Leaf Blight", "common_name": "Grape — Leaf Blight (Isariopsis leaf spot)",
        "is_healthy": False,
        "cause": "Fungal pathogen favored by prolonged leaf wetness.",
        "symptoms": "Dark angular lesions running along leaf veins.",
        "treatment": "Copper-based fungicide, prune for airflow, avoid overhead irrigation.",
    },

    # ---------------- Apple Classes ----------------
    "Apple___healthy": {
        "plant": "Apple", "disease": "Healthy", "common_name": "Apple — Healthy Leaf",
        "is_healthy": True, "cause": "N/A (Plant is in optimal vigor)",
        "symptoms": "Glossy uniform green leaves.",
        "treatment": "Routine pruning and balanced fertilization.",
    },
    "Apple___Apple_scab": {
        "plant": "Apple", "disease": "Apple Scab", "common_name": "Apple — Scab (Venturia inaequalis)",
        "is_healthy": False,
        "cause": "Venturia inaequalis, favored by cool wet spring weather.",
        "symptoms": "Olive-green to black velvety spots on leaves and fruit.",
        "treatment": "Captan or myclobutanil sprays timed to bud break; rake and destroy fallen leaves.",
    },
    "Apple___Cedar_apple_rust": {
        "plant": "Apple", "disease": "Cedar Apple Rust", "common_name": "Apple — Cedar Apple Rust",
        "is_healthy": False,
        "cause": "Fungus alternating between apple and nearby juniper/cedar hosts.",
        "symptoms": "Bright orange-yellow spots on the upper leaf surface.",
        "treatment": "Remove nearby juniper hosts where feasible; apply protective fungicide in spring.",
    },

    # ---------------- Strawberry Classes ----------------
    "Strawberry___healthy": {
        "plant": "Strawberry", "disease": "Healthy", "common_name": "Strawberry — Healthy Leaf",
        "is_healthy": True, "cause": "N/A (Plant is in optimal vigor)",
        "symptoms": "Bright green trifoliate leaves.",
        "treatment": "Balanced fertigation and mulching.",
    },
    "Strawberry___Leaf_scorch": {
        "plant": "Strawberry", "disease": "Leaf Scorch", "common_name": "Strawberry — Leaf Scorch (Diplocarpon earlianum)",
        "is_healthy": False,
        "cause": "Diplocarpon earlianum, favored by humid conditions.",
        "symptoms": "Small purple blotches merging into scorched, dried patches.",
        "treatment": "Remove infected leaves post-harvest; captan/myclobutanil spray; avoid overhead watering.",
    },

    # ---------------- Local Demonstrator Classes: Money Plant / Money Tree ----------------
    "Money_Plant___healthy": {
        "plant": "Money Plant (Epipremnum aureum)",
        "disease": "Healthy",
        "common_name": "Money Plant — Healthy Foliage",
        "is_healthy": True,
        "cause": "N/A (Optimal chlorophyll synthesis and cellular turgor)",
        "symptoms": "Vibrant glossy green heart-shaped leaves with distinct variegation, firm supple petiole.",
        "treatment": "Maintain bright indirect sunlight; water only when upper 2 inches of potting mix dry out."
    },
    "Money_Plant___leaf_spot": {
        "plant": "Money Plant (Epipremnum aureum)",
        "disease": "Bacterial / Fungal Leaf Spot",
        "common_name": "Money Plant — Leaf Spot (Colletotrichum / Pseudomonas)",
        "is_healthy": False,
        "cause": "Fungal spore colonization or bacterial ingress exacerbated by prolonged foliar moisture and poor ventilation.",
        "symptoms": "Brown, black, or tan water-soaked circular necrotic spots with pronounced yellow chlorotic halo rings.",
        "treatment": "Immediately isolate plant; prune severely affected foliage; apply copper hydroxide or organic neem oil foliar spray (2ml/L); cease overhead leaf misting."
    },
    "Money_Plant___yellowing": {
        "plant": "Money Plant (Epipremnum aureum)",
        "disease": "Chlorosis / Overwatering Root Hypoxia",
        "common_name": "Money Plant — Leaf Yellowing (Chlorosis)",
        "is_healthy": False,
        "cause": "Root oxygen starvation due to over-saturation of root zone, or nitrogen/iron micronutrient deficiency.",
        "symptoms": "Diffused pale yellowing across leaf lamina, softening of lower leaf stems, loss of structural rigidity.",
        "treatment": "Allow potting medium to aerate and dry; ensure container drainage holes are clear; apply balanced water-soluble micronutrient fertilizer (20-20-20 NPK)."
    },
    "Money_Tree___healthy": {
        "plant": "Money Tree (Pachira aquatica)",
        "disease": "Healthy",
        "common_name": "Money Tree — Healthy Foliage",
        "is_healthy": True,
        "cause": "N/A (Optimal plant vigor and root aeration)",
        "symptoms": "Lush umbrella-like palmate compound leaflets with rich uniform green coloration.",
        "treatment": "Place in bright indirect light; deep watering every 1-2 weeks allowing soil to partially dry."
    },
    "Money_Tree___leaf_spot": {
        "plant": "Money Tree (Pachira aquatica)",
        "disease": "Leaf Spot / Anthracnose",
        "common_name": "Money Tree — Anthracnose Leaf Spot",
        "is_healthy": False,
        "cause": "Colletotrichum fungal infection under warm, stagnant humid microclimates.",
        "symptoms": "Irregular dark reddish-brown lesions with yellow margins expanding along leaflet veins.",
        "treatment": "Prune spotted leaflets; treat with copper-based or bio-fungicide (Trichoderma); improve cross-ventilation."
    },

    # ---------------- Background Non-Leaf ----------------
    "background_not_a_leaf": {
        "plant": "Non-Plant / Background",
        "disease": "N/A",
        "common_name": "Background / Non-Leaf Image",
        "is_healthy": False,
        "cause": "Camera focused on soil, rocks, sky, hands, or agricultural robot chassis.",
        "symptoms": "Frame does not contain valid plant leaf foliage.",
        "treatment": "Reposition rover camera directly above target plant canopy."
    },

    # ---------------- Tulsi (Holy Basil) Classes (PlantVita Dataset) ----------------
    "Tulsi___Healthy": {
        "plant": "Tulsi (Holy Basil)",
        "disease": "Healthy",
        "common_name": "Tulsi — Healthy Foliage",
        "is_healthy": True,
        "cause": "Optimal physiological health; appropriate sunlight (4-6 hrs) and well-draining soil.",
        "symptoms": "Aromatic, deep green, tender leaves with no necrotic lesions, yellowing, or pest damage.",
        "treatment": "Maintain regular watering when topsoil dries; pinch flower buds periodically to encourage bushier leaf growth."
    },
    "Tulsi___healthy": {
        "plant": "Tulsi (Holy Basil)",
        "disease": "Healthy",
        "common_name": "Tulsi — Healthy Foliage",
        "is_healthy": True,
        "cause": "Optimal physiological health; appropriate sunlight and well-draining soil.",
        "symptoms": "Aromatic, deep green, tender leaves with no necrotic lesions, yellowing, or pest damage.",
        "treatment": "Maintain regular watering when topsoil dries; pinch flower buds periodically to encourage bushier leaf growth."
    },
    "Tulsi___Infected": {
        "plant": "Tulsi (Holy Basil)",
        "disease": "Fungal / Bacterial Infection (Leaf Spot & Blight)",
        "common_name": "Tulsi — Leaf Infection (Cercospora / Corynespora)",
        "is_healthy": False,
        "cause": "Fungal or bacterial pathogen favored by water splashing on leaves, dense canopy, and stagnant damp air.",
        "symptoms": "Brown, black, or water-soaked necrotic spots on leaf blades, concentric rings with chlorotic halos, defoliation.",
        "treatment": "Prune infected leaves immediately; avoid overhead watering; spray organic 0.5% Neem oil solution or copper oxychloride fungicide every 7 days."
    },
    "Tulsi___leaf_spot": {
        "plant": "Tulsi (Holy Basil)",
        "disease": "Leaf Spot / Blight",
        "common_name": "Tulsi — Leaf Infection (Cercospora / Corynespora)",
        "is_healthy": False,
        "cause": "Fungal or bacterial pathogen favored by water splashing on leaves, dense canopy, and stagnant damp air.",
        "symptoms": "Brown, black, or water-soaked necrotic spots on leaf blades, concentric rings with chlorotic halos, defoliation.",
        "treatment": "Prune infected leaves immediately; avoid overhead watering; spray organic 0.5% Neem oil solution or copper oxychloride fungicide every 7 days."
    },
    "Tulsi___Infested": {
        "plant": "Tulsi (Holy Basil)",
        "disease": "Pest Infestation (Aphids / Mealybugs / Spider Mites)",
        "common_name": "Tulsi — Insect Pest Infestation",
        "is_healthy": False,
        "cause": "Sap-sucking arthropod pests (aphids, thrips, spider mites, or mealybugs) colonizing leaf undersides and tender shoots.",
        "symptoms": "Curled or puckered leaves, white waxy residue or fine webbing under leaves, sticky honeydew secretion, stippling.",
        "treatment": "Wash foliage with a firm spray of water; apply insecticidal soap spray or cold-pressed Neem oil (5ml/L + mild organic soap); introduce ladybug predators."
    },
    "Tulsi___Wilting": {
        "plant": "Tulsi (Holy Basil)",
        "disease": "Wilting (Fusarium Wilt / Root Stress)",
        "common_name": "Tulsi — Vascular Wilt & Root Stress",
        "is_healthy": False,
        "cause": "Fusarium oxysporum soil fungus or acute root asphyxiation from waterlogged soil / blocked drainage holes.",
        "symptoms": "Drooping, limp, flaccid foliage despite damp soil; brown vascular discoloration inside lower stem; sudden leaf collapse.",
        "treatment": "Stop overwatering immediately; ensure pot drainage is clear; drench soil with Trichoderma viride bio-fungicide; repot in sterile porous potting mix if root rot is observed."
    },

    # ---------------- Money Plant (Pothos) Classes ----------------
    "Money_Plant___healthy": {
        "plant": "Money Plant (Golden Pothos)",
        "disease": "Healthy",
        "common_name": "Money Plant — Healthy Foliage",
        "is_healthy": True,
        "cause": "Proper indirect sunlight, porous soil medium, and balanced moisture levels.",
        "symptoms": "Glossy, heart-shaped vibrant green leaves with natural golden variegation, firm petioles.",
        "treatment": "Keep in bright indirect light; allow upper 1-2 inches of soil to dry between waterings; wipe dust from foliage."
    },
    "Money_Plant___leaf_spot": {
        "plant": "Money Plant (Golden Pothos)",
        "disease": "Leaf Spot (Bacterial / Fungal)",
        "common_name": "Money Plant — Leaf Spot",
        "is_healthy": False,
        "cause": "Pseudomonas or Rhizoctonia pathogen promoted by humid, poorly ventilated indoor environments.",
        "symptoms": "Water-soaked dark brown spots with translucent yellow borders on leaf blades.",
        "treatment": "Isolate plant; remove diseased leaves; apply copper fungicide or neem oil; avoid misting leaves indoors."
    },
    "Money_Plant___yellowing": {
        "plant": "Money Plant (Golden Pothos)",
        "disease": "Chlorosis / Overwatering",
        "common_name": "Money Plant — Leaf Chlorosis",
        "is_healthy": False,
        "cause": "Waterlogged root zone leading to oxygen deprivation, or nitrogen/iron nutrient deficiency.",
        "symptoms": "Diffuse yellowing across leaf surface, limp leaves, mushy petiole bases.",
        "treatment": "Reduce irrigation frequency; verify pot has functional drainage; feed with balanced liquid houseplant fertilizer."
    },
    # ---------------- Local Live Field Demonstration Classes ----------------
    "Local_healthy": {
        "plant": "Local Plant (Duranta / Tulsi)",
        "disease": "Healthy",
        "common_name": "Local Plant — Healthy Foliage Vigor",
        "is_healthy": True,
        "cause": "Optimal physiological hydration, proper ambient sunlight exposure, and balanced soil nutrient uptake.",
        "symptoms": "Vibrant emerald green leaf blade, intact cuticle layer, firm petiole, complete absence of chlorosis or necrotic spotting.",
        "treatment": "Maintain current automated drip irrigation schedule; ensure 4-6 hours of daily sunlight; supplement monthly with organic vermicompost."
    },
    "Local_unhealthy": {
        "plant": "Local Plant (Duranta / Tulsi)",
        "disease": "Foliar Leaf Spot / Blight",
        "common_name": "Local Plant — Leaf Spot Blight (Cercospora / Bacterial)",
        "is_healthy": False,
        "cause": "Foliar fungal pathogen (Cercospora / Colletotrichum spp.) or bacterial blight, promoted by foliage dampness and poor air circulation.",
        "symptoms": "Irregular dark brown to charcoal necrotic lesions across the leaf lamina, water-soaked margins, and cellular tissue decay.",
        "treatment": "Prune and safely discard heavily spotted leaves; avoid overhead watering; apply organic Neem oil spray (5 ml/L with liquid soap) or foliar Copper Oxychloride (COC 50% WP @ 2.5 g/L)."
    },
    "Local_yellow": {
        "plant": "Local Plant (Duranta / Tulsi)",
        "disease": "Chlorosis / Nutrient Deficiency",
        "common_name": "Local Plant — Leaf Chlorosis (Yellowing)",
        "is_healthy": False,
        "cause": "Chlorophyll breakdown caused by nitrogen/iron/magnesium nutrient deficiency, or root waterlogging from over-irrigation.",
        "symptoms": "Distinct golden-yellow to pale lime discoloration across leaf blade with green central venation (interveinal chlorosis) or edge chlorosis.",
        "treatment": "Allow topsoil to dry before watering (let AgroNex hysteresis cycle control pump); apply balanced N-P-K 19-19-19 liquid fertilizer; supplement with Epsom salt (Magnesium sulfate @ 5 g/L) and chelated iron (Fe-EDTA)."
    },
    "Local_dried": {
        "plant": "Local Plant (Duranta / Tulsi)",
        "disease": "Desiccation / Severe Moisture Stress",
        "common_name": "Local Plant — Desiccation & Wilting (Drought / Root Rot)",
        "is_healthy": False,
        "cause": "Severe soil drought, prolonged moisture deprivation, root-bound soil, or vascular wilt restricting water transport.",
        "symptoms": "Inward longitudinal leaf curling, brittle papery texture, dry brown margins, and complete loss of cellular turgidity.",
        "treatment": "Initiate immediate deep root irrigation; verify soil moisture sensor probe calibration; apply organic mulch (dry straw or wood chips) around plant base to conserve soil moisture; if roots are decaying, drench soil with Trichoderma bio-fungicide."
    },
    "background_not_a_leaf": {
        "plant": "Non-Crop Surface",
        "disease": "Not a Leaf",
        "common_name": "Non-Leaf Background (Soil / Table / Chassis)",
        "is_healthy": True,
        "cause": "Camera is pointed at garden soil, tabletop, floor, pot rim, or rover chassis.",
        "symptoms": "No plant leaf structure or green vegetation detected in current frame.",
        "treatment": "Reposition rover camera toward plant foliage for crop disease analysis."
    }
}



def get_disease_info(label: str) -> dict:
    """Returns disease detail dictionary for a given label string."""
    if not label:
        label = "background_not_a_leaf"
        
    if label in DISEASE_KNOWLEDGE_BASE:
        return DISEASE_KNOWLEDGE_BASE[label]
    
    # Try normalized matching
    normalized = label.strip().replace(" ", "_")
    for key, val in DISEASE_KNOWLEDGE_BASE.items():
        if key.lower() == normalized.lower():
            return val
            
    # Heuristic parsing fallback
    plant = "Plant Leaf"
    disease = "Unknown Condition"
    is_healthy = "healthy" in label.lower()
    
    lbl = label.lower()
    if "tulsi" in lbl or "holy_basil" in lbl or "basil" in lbl:
        plant = "Tulsi (Holy Basil)"
    elif "money" in lbl or "pothos" in lbl:
        plant = "Money Plant"
    elif "tomato" in lbl:
        plant = "Tomato"
    elif "potato" in lbl:
        plant = "Potato"
    elif "pepper" in lbl:
        plant = "Bell Pepper"
        
    if is_healthy:
        disease = "Healthy"
    elif "infest" in lbl or "pest" in lbl or "bug" in lbl:
        disease = "Pest Infestation"
    elif "wilt" in lbl:
        disease = "Wilting / Root Stress"
    elif "infect" in lbl or "spot" in lbl or "blight" in lbl:
        disease = "Leaf Infection / Spot"
    elif "yellow" in lbl or "chlorosis" in lbl:
        disease = "Yellowing / Chlorosis"
    elif "mildew" in lbl:
        disease = "Powdery Mildew"
        
    return {
        "plant": plant,
        "disease": disease,
        "common_name": f"{plant} — {disease}",
        "is_healthy": is_healthy,
        "cause": "Pathogen diagnostic record in progress.",
        "symptoms": "Visual anomalies detected on leaf tissue.",
        "treatment": "Consult local agricultural extension service for targeted agronomic recommendations."
    }


