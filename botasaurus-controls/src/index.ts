function isEmptyObject(obj: any) {
  return !Object.keys(obj).length && obj.constructor === Object
}

function isNullish(x: any) {
  return x === null || x === undefined
}
function isEmpty(x: any) {
  return (
    x === null || x === undefined || (typeof x == "string" && x.trim() === "")
  )
}


function isNotEmpty(x: any) {
  return !isEmpty(x)
}


function ensureEndsWithDot(validationResult: string): string {
  return validationResult.endsWith(".")
    ? validationResult
    : validationResult + "."
}

function ensureNotEndsWithDot(validationResult: string): string {
  return validationResult.endsWith(".")
    ? validationResult.slice(0, -1)
    : validationResult
}

function sentenceCase(string: string) {
  // Convert a string into Sentence case.
  if (!string) {
    return ""
  }
  // Add space between separators and numbers
  string = string
    .split(/([\W_\d])/)
    .filter((s: any) => s)
    .join(" ")
  // Remove separators (except numbers)
  string = string.replace(/[\W_]/g, " ").split(/\s+/).join(" ")
  // Manage capital letters and capitalize the first character
  return string
    .replace(/([A-Z])/g, " $1")
    .trim()
    .replace(/^\w/, (c: string) => c.toUpperCase())
}
function isValidHttpUrl(string: any) {
  let url: any

  try {
    url = new URL(string)
  } catch (_) {
    return false
  }

  return url.protocol === "http:" || url.protocol === "https:"
}

function ensureListOfStrings(value: any, id: string): string[] {
  if (!Array.isArray(value)) {
    throw new Error(
      `DefaultValue for control '${id}' must be an array of strings.`
    )
  }

  const isAllStrings = value.every((item) => typeof item === "string")
  if (!isAllStrings) {
    throw new Error(
      `All items in the defaultValue array for control '${id}' must be strings.`
    )
  }

  return value
}



function isNotValidSelectOrChooseValue(value: any, control: Control<any, WithChooseOptions>) {
  // @ts-ignore
    return value && !control.options.some((option) => option.value === value)
  }
  
  function hasOptions(type: string) {
    return type === "select" || type === "choose"
  }
  
function isFunc(isRequired: any) {
  return typeof isRequired === "function"
}

function canTrim(control: Control<any, WithChooseOptions>) {
  // @ts-ignore
  return isNullish(control.trim) || control.trim !== false
}

function convertToBool(isRequired?: boolean | ((data: any) => boolean), data?: any): boolean {
  if (typeof isRequired === "boolean") {
    return isRequired
  } else if (isFunc(isRequired)) {
    // @ts-ignore
    return !!isRequired(data)
  } else {
    return false
  }
}
// Define a generic control type with an additional parameter P for custom properties
type ControlInput<V, P = {}> = {
  label?: string // Label is now optional
  defaultValue?: V
  helpText?: string
  isRequired?: boolean | ((data: any) => boolean) // Property to indicate if the control is required
  isDisabled?: (data: any) => boolean
  disabledMessage?: string,
  isShown?: (data: any) => boolean
  isMetadata?: boolean
  validate?: (value: V, otherData: any) => string | string[] | undefined
} & P // Merge P with the rest of the control input properties

// Define a generic control type with an additional parameter P for custom properties
type TextControlInput<V, P = {}> = ControlInput<V, P> & {
  // defaults to true
  trim?: boolean
  placeholder?: string
}

type LinkControlInput<V, P = {}> = ControlInput<V, P> & {
  placeholder?: string
}

// Define a generic control type with an additional parameter P for custom properties
type NumberControlInput<V, P = {}> = ControlInput<V, P> & {
  placeholder?: string
  min?: number
  max?: number
}

// Define a type for options
type Option = {
  value: string
  label: string
}

type ChooseOption = Option

// Define a type for control properties that include options
export type WithChooseOptions = {
  options?: ChooseOption[]
}

// Define a type for control properties that include options
type WithOptions = {
  options?: Option[]
}

export type Control<V, P = {}> = {
  id: string
  type: string
  label: string
} & ControlInput<V, P> // Merge ControlInput properties with control-specific properties


function getDefaultLanguages() {
  return [{ "value": "en", "label": "English" }, { "value": "es", "label": "Spanish" }, { "value": "ja", "label": "Japanese" }, { "value": "fr", "label": "French" }, { "value": "it", "label": "Italian" }, { "value": "hi", "label": "Hindi" }, { "value": "ab", "label": "Abkhazian" }, { "value": "aa", "label": "Afar" }, { "value": "af", "label": "Afrikaans" }, { "value": "ak", "label": "Akan" }, { "value": "sq", "label": "Albanian" }, { "value": "am", "label": "Amharic" }, { "value": "ar", "label": "Arabic" }, { "value": "an", "label": "Aragonese" }, { "value": "hy", "label": "Armenian" }, { "value": "as", "label": "Assamese" }, { "value": "av", "label": "Avar" }, { "value": "ay", "label": "Aymara" }, { "value": "az", "label": "Azerbaijani" }, { "value": "bm", "label": "Bambara" }, { "value": "ba", "label": "Bashkir" }, { "value": "eu", "label": "Basque" }, { "value": "be", "label": "Belarusian" }, { "value": "bn", "label": "Bengali" }, { "value": "bh", "label": "Bihari" }, { "value": "bi", "label": "Bislama" }, { "value": "bs", "label": "Bosnian" }, { "value": "br", "label": "Breton" }, { "value": "bg", "label": "Bulgarian" }, { "value": "my", "label": "Burmese" }, { "value": "km", "label": "Cambodian" }, { "value": "ca", "label": "Catalan" }, { "value": "ch", "label": "Chamorro" }, { "value": "ce", "label": "Chechen" }, { "value": "ny", "label": "Chichewa" }, { "value": "cv", "label": "Chuvash" }, { "value": "kw", "label": "Cornish" }, { "value": "co", "label": "Corsican" }, { "value": "cr", "label": "Cree" }, { "value": "hr", "label": "Croatian" }, { "value": "cs", "label": "Czech" }, { "value": "da", "label": "Danish" }, { "value": "dv", "label": "Divehi" }, { "value": "nl", "label": "Dutch" }, { "value": "dz", "label": "Dzongkha" }, { "value": "eo", "label": "Esperanto" }, { "value": "et", "label": "Estonian" }, { "value": "ee", "label": "Ewe" }, { "value": "fo", "label": "Faroese" }, { "value": "fj", "label": "Fijian" }, { "value": "fi", "label": "Finnish" }, { "value": "gl", "label": "Galician" }, { "value": "lg", "label": "Ganda" }, { "value": "ka", "label": "Georgian" }, { "value": "de", "label": "German" }, { "value": "el", "label": "Greek" }, { "value": "kl", "label": "Greenlandic" }, { "value": "gn", "label": "Guarani" }, { "value": "gu", "label": "Gujarati" }, { "value": "ht", "label": "Haitian" }, { "value": "ha", "label": "Hausa" }, { "value": "he", "label": "Hebrew" }, { "value": "hz", "label": "Herero" }, { "value": "ho", "label": "Hiri Motu" }, { "value": "hu", "label": "Hungarian" }, { "value": "is", "label": "Icelandic" }, { "value": "io", "label": "Ido" }, { "value": "ig", "label": "Igbo" }, { "value": "id", "label": "Indonesian" }, { "value": "ia", "label": "Interlingua" }, { "value": "ie", "label": "Interlingue" }, { "value": "iu", "label": "Inuktitut" }, { "value": "ik", "label": "Inupiak" }, { "value": "ga", "label": "Irish" }, { "value": "jv", "label": "Javanese" }, { "value": "kn", "label": "Kannada" }, { "value": "kr", "label": "Kanuri" }, { "value": "ks", "label": "Kashmiri" }, { "value": "kk", "label": "Kazakh" }, { "value": "ki", "label": "Kikuyu" }, { "value": "rn", "label": "Kirundi" }, { "value": "kv", "label": "Komi" }, { "value": "kg", "label": "Kongo" }, { "value": "ko", "label": "Korean" }, { "value": "kj", "label": "Kuanyama" }, { "value": "ku", "label": "Kurdish" }, { "value": "ky", "label": "Kyrgyz" }, { "value": "lo", "label": "Laotian" }, { "value": "la", "label": "Latin" }, { "value": "lv", "label": "Latvian" }, { "value": "li", "label": "Limburgian" }, { "value": "ln", "label": "Lingala" }, { "value": "lt", "label": "Lithuanian" }, { "value": "lu", "label": "Luba Katanga" }, { "value": "lb", "label": "Luxembourgish" }, { "value": "mk", "label": "Macedonian" }, { "value": "mg", "label": "Malagasy" }, { "value": "ms", "label": "Malay" }, { "value": "ml", "label": "Malayalam" }, { "value": "mt", "label": "Maltese" }, { "value": "gv", "label": "Manx" }, { "value": "mi", "label": "Maori" }, { "value": "mr", "label": "Marathi" }, { "value": "mh", "label": "Marshallese" }, { "value": "mo", "label": "Moldovan" }, { "value": "mn", "label": "Mongolian" }, { "value": "na", "label": "Nauruan" }, { "value": "nv", "label": "Navajo" }, { "value": "ng", "label": "Ndonga" }, { "value": "ne", "label": "Nepali" }, { "value": "se", "label": "Northern Sami" }, { "value": "nd", "label": "North Ndebele" }, { "value": "no", "label": "Norwegian" }, { "value": "nb", "label": "Norwegian Bokmål" }, { "value": "nn", "label": "Norwegian Nynorsk" }, { "value": "oc", "label": "Occitan" }, { "value": "oj", "label": "Ojibwa" }, { "value": "cu", "label": "Old Church Slavonic" }, { "value": "or", "label": "Oriya" }, { "value": "om", "label": "Oromo" }, { "value": "os", "label": "Ossetic" }, { "value": "pi", "label": "Pali" }, { "value": "ps", "label": "Pashto" }, { "value": "fa", "label": "Persian" }, { "value": "ff", "label": "Peul" }, { "value": "pl", "label": "Polish" }, { "value": "pt", "label": "Portuguese" }, { "value": "pa", "label": "Punjabi" }, { "value": "qu", "label": "Quechua" }, { "value": "rm", "label": "Raeto Romance" }, { "value": "ro", "label": "Romanian" }, { "value": "ru", "label": "Russian" }, { "value": "rw", "label": "Rwandi" }, { "value": "sm", "label": "Samoan" }, { "value": "sg", "label": "Sango" }, { "value": "sa", "label": "Sanskrit" }, { "value": "sc", "label": "Sardinian" }, { "value": "gd", "label": "Scottish Gaelic" }, { "value": "sr", "label": "Serbian" }, { "value": "sh", "label": "Serbo Croatian" }, { "value": "sn", "label": "Shona" }, { "value": "ii", "label": "Sichuan Yi" }, { "value": "sd", "label": "Sindhi" }, { "value": "si", "label": "Sinhalese" }, { "value": "sk", "label": "Slovak" }, { "value": "sl", "label": "Slovenian" }, { "value": "so", "label": "Somalia" }, { "value": "st", "label": "Southern Sotho" }, { "value": "nr", "label": "South Ndebele" }, { "value": "su", "label": "Sundanese" }, { "value": "sw", "label": "Swahili" }, { "value": "ss", "label": "Swati" }, { "value": "sv", "label": "Swedish" }, { "value": "tl", "label": "Tagalog" }, { "value": "ty", "label": "Tahitian" }, { "value": "tg", "label": "Tajik" }, { "value": "ta", "label": "Tamil" }, { "value": "tt", "label": "Tatar" }, { "value": "te", "label": "Telugu" }, { "value": "th", "label": "Thai" }, { "value": "bo", "label": "Tibetan" }, { "value": "ti", "label": "Tigrinya" }, { "value": "to", "label": "Tonga" }, { "value": "ts", "label": "Tsonga" }, { "value": "tn", "label": "Tswana" }, { "value": "tr", "label": "Turkish" }, { "value": "tk", "label": "Turkmen" }, { "value": "tw", "label": "Twi" }, { "value": "uk", "label": "Ukrainian" }, { "value": "ur", "label": "Urdu" }, { "value": "ug", "label": "Uyghur" }, { "value": "uz", "label": "Uzbek" }, { "value": "ve", "label": "Venda" }, { "value": "vi", "label": "Vietnamese" }, { "value": "vo", "label": "Volapük" }, { "value": "wa", "label": "Walloon" }, { "value": "cy", "label": "Welsh" }, { "value": "fy", "label": "West Frisian" }, { "value": "wo", "label": "Wolof" }, { "value": "xh", "label": "Xhosa" }, { "value": "yi", "label": "Yiddish" }, { "value": "yo", "label": "Yoruba" }, { "value": "za", "label": "Zhuang" }, { "value": "zu", "label": "Zulu" }]
}

function getDefaultCountries() {
  return [{ "value": "AF", "label": "Afghanistan" }, { "value": "AX", "label": "Aland Islands" }, { "value": "AL", "label": "Albania" }, { "value": "DZ", "label": "Algeria" }, { "value": "AS", "label": "American Samoa" }, { "value": "AD", "label": "Andorra" }, { "value": "AO", "label": "Angola" }, { "value": "AI", "label": "Anguilla" }, { "value": "AQ", "label": "Antarctica" }, { "value": "AG", "label": "Antigua And Barbuda" }, { "value": "AR", "label": "Argentina" }, { "value": "AM", "label": "Armenia" }, { "value": "AW", "label": "Aruba" }, { "value": "AU", "label": "Australia" }, { "value": "AT", "label": "Austria" }, { "value": "AZ", "label": "Azerbaijan" }, { "value": "BS", "label": "Bahamas" }, { "value": "BH", "label": "Bahrain" }, { "value": "BD", "label": "Bangladesh" }, { "value": "BB", "label": "Barbados" }, { "value": "BY", "label": "Belarus" }, { "value": "BE", "label": "Belgium" }, { "value": "BZ", "label": "Belize" }, { "value": "BJ", "label": "Benin" }, { "value": "BM", "label": "Bermuda" }, { "value": "BT", "label": "Bhutan" }, { "value": "BO", "label": "Bolivia" }, { "value": "BQ", "label": "Bonaire Saint Eustatius And Saba" }, { "value": "BA", "label": "Bosnia And Herzegovina" }, { "value": "BW", "label": "Botswana" }, { "value": "BV", "label": "Bouvet Island" }, { "value": "BR", "label": "Brazil" }, { "value": "IO", "label": "British Indian Ocean Territory" }, { "value": "VG", "label": "British Virgin Islands" }, { "value": "BN", "label": "Brunei" }, { "value": "BG", "label": "Bulgaria" }, { "value": "BF", "label": "Burkina Faso" }, { "value": "BI", "label": "Burundi" }, { "value": "CV", "label": "Cabo Verde" }, { "value": "KH", "label": "Cambodia" }, { "value": "CM", "label": "Cameroon" }, { "value": "CA", "label": "Canada" }, { "value": "KY", "label": "Cayman Islands" }, { "value": "CF", "label": "Central African Republic" }, { "value": "TD", "label": "Chad" }, { "value": "CL", "label": "Chile" }, { "value": "CN", "label": "China" }, { "value": "CX", "label": "Christmas Island" }, { "value": "CC", "label": "Cocos Islands" }, { "value": "CO", "label": "Colombia" }, { "value": "KM", "label": "Comoros" }, { "value": "CK", "label": "Cook Islands" }, { "value": "CR", "label": "Costa Rica" }, { "value": "HR", "label": "Croatia" }, { "value": "CU", "label": "Cuba" }, { "value": "CW", "label": "Curacao" }, { "value": "CY", "label": "Cyprus" }, { "value": "CZ", "label": "Czechia" }, { "value": "CD", "label": "Democratic Republic Of The Congo" }, { "value": "DK", "label": "Denmark" }, { "value": "DJ", "label": "Djibouti" }, { "value": "DM", "label": "Dominica" }, { "value": "DO", "label": "Dominican Republic" }, { "value": "EC", "label": "Ecuador" }, { "value": "EG", "label": "Egypt" }, { "value": "SV", "label": "El Salvador" }, { "value": "GQ", "label": "Equatorial Guinea" }, { "value": "ER", "label": "Eritrea" }, { "value": "EE", "label": "Estonia" }, { "value": "SZ", "label": "Eswatini" }, { "value": "ET", "label": "Ethiopia" }, { "value": "FK", "label": "Falkland Islands" }, { "value": "FO", "label": "Faroe Islands" }, { "value": "FJ", "label": "Fiji" }, { "value": "FI", "label": "Finland" }, { "value": "FR", "label": "France" }, { "value": "GF", "label": "French Guiana" }, { "value": "PF", "label": "French Polynesia" }, { "value": "TF", "label": "French Southern Territories" }, { "value": "GA", "label": "Gabon" }, { "value": "GM", "label": "Gambia" }, { "value": "GE", "label": "Georgia" }, { "value": "DE", "label": "Germany" }, { "value": "GH", "label": "Ghana" }, { "value": "GI", "label": "Gibraltar" }, { "value": "GR", "label": "Greece" }, { "value": "GL", "label": "Greenland" }, { "value": "GD", "label": "Grenada" }, { "value": "GP", "label": "Guadeloupe" }, { "value": "GU", "label": "Guam" }, { "value": "GT", "label": "Guatemala" }, { "value": "GG", "label": "Guernsey" }, { "value": "GN", "label": "Guinea" }, { "value": "GW", "label": "Guinea Bissau" }, { "value": "GY", "label": "Guyana" }, { "value": "HT", "label": "Haiti" }, { "value": "HM", "label": "Heard Island And Mc Donald Islands" }, { "value": "HN", "label": "Honduras" }, { "value": "HK", "label": "Hong Kong" }, { "value": "HU", "label": "Hungary" }, { "value": "IS", "label": "Iceland" }, { "value": "IN", "label": "India" }, { "value": "ID", "label": "Indonesia" }, { "value": "IR", "label": "Iran" }, { "value": "IQ", "label": "Iraq" }, { "value": "IE", "label": "Ireland" }, { "value": "IM", "label": "Isle Of Man" }, { "value": "IL", "label": "Israel" }, { "value": "IT", "label": "Italy" }, { "value": "CI", "label": "Ivory Coast" }, { "value": "JM", "label": "Jamaica" }, { "value": "JP", "label": "Japan" }, { "value": "JE", "label": "Jersey" }, { "value": "JO", "label": "Jordan" }, { "value": "KZ", "label": "Kazakhstan" }, { "value": "KE", "label": "Kenya" }, { "value": "KI", "label": "Kiribati" }, { "value": "XK", "label": "Kosovo" }, { "value": "KW", "label": "Kuwait" }, { "value": "KG", "label": "Kyrgyzstan" }, { "value": "LA", "label": "Laos" }, { "value": "LV", "label": "Latvia" }, { "value": "LB", "label": "Lebanon" }, { "value": "LS", "label": "Lesotho" }, { "value": "LR", "label": "Liberia" }, { "value": "LY", "label": "Libya" }, { "value": "LI", "label": "Liechtenstein" }, { "value": "LT", "label": "Lithuania" }, { "value": "LU", "label": "Luxembourg" }, { "value": "MO", "label": "Macao" }, { "value": "MG", "label": "Madagascar" }, { "value": "MW", "label": "Malawi" }, { "value": "MY", "label": "Malaysia" }, { "value": "MV", "label": "Maldives" }, { "value": "ML", "label": "Mali" }, { "value": "MT", "label": "Malta" }, { "value": "MH", "label": "Marshall Islands" }, { "value": "MQ", "label": "Martinique" }, { "value": "MR", "label": "Mauritania" }, { "value": "MU", "label": "Mauritius" }, { "value": "YT", "label": "Mayotte" }, { "value": "MX", "label": "Mexico" }, { "value": "FM", "label": "Micronesia" }, { "value": "MD", "label": "Moldova" }, { "value": "MC", "label": "Monaco" }, { "value": "MN", "label": "Mongolia" }, { "value": "ME", "label": "Montenegro" }, { "value": "MS", "label": "Montserrat" }, { "value": "MA", "label": "Morocco" }, { "value": "MZ", "label": "Mozambique" }, { "value": "MM", "label": "Myanmar" }, { "value": "NA", "label": "Namibia" }, { "value": "NR", "label": "Nauru" }, { "value": "NP", "label": "Nepal" }, { "value": "NL", "label": "Netherlands" }, { "value": "AN", "label": "Netherlands Antilles" }, { "value": "NC", "label": "New Caledonia" }, { "value": "NZ", "label": "New Zealand" }, { "value": "NI", "label": "Nicaragua" }, { "value": "NE", "label": "Niger" }, { "value": "NG", "label": "Nigeria" }, { "value": "NU", "label": "Niue" }, { "value": "NF", "label": "Norfolk Island" }, { "value": "MP", "label": "Northern Mariana Islands" }, { "value": "KP", "label": "North Korea" }, { "value": "MK", "label": "North Macedonia" }, { "value": "NO", "label": "Norway" }, { "value": "OM", "label": "Oman" }, { "value": "PK", "label": "Pakistan" }, { "value": "PW", "label": "Palau" }, { "value": "PS", "label": "Palestinian Territory" }, { "value": "PA", "label": "Panama" }, { "value": "PG", "label": "Papua New Guinea" }, { "value": "PY", "label": "Paraguay" }, { "value": "PE", "label": "Peru" }, { "value": "PH", "label": "Philippines" }, { "value": "PN", "label": "Pitcairn" }, { "value": "PL", "label": "Poland" }, { "value": "PT", "label": "Portugal" }, { "value": "PR", "label": "Puerto Rico" }, { "value": "QA", "label": "Qatar" }, { "value": "CG", "label": "Republic Of The Congo" }, { "value": "RE", "label": "Reunion" }, { "value": "RO", "label": "Romania" }, { "value": "RU", "label": "Russia" }, { "value": "RW", "label": "Rwanda" }, { "value": "BL", "label": "Saint Barthelemy" }, { "value": "SH", "label": "Saint Helena" }, { "value": "KN", "label": "Saint Kitts And Nevis" }, { "value": "LC", "label": "Saint Lucia" }, { "value": "MF", "label": "Saint Martin" }, { "value": "PM", "label": "Saint Pierre And Miquelon" }, { "value": "VC", "label": "Saint Vincent And The Grenadines" }, { "value": "WS", "label": "Samoa" }, { "value": "SM", "label": "San Marino" }, { "value": "ST", "label": "Sao Tome And Principe" }, { "value": "SA", "label": "Saudi Arabia" }, { "value": "SN", "label": "Senegal" }, { "value": "RS", "label": "Serbia" }, { "value": "CS", "label": "Serbia And Montenegro" }, { "value": "SC", "label": "Seychelles" }, { "value": "SL", "label": "Sierra Leone" }, { "value": "SG", "label": "Singapore" }, { "value": "SX", "label": "Sint Maarten" }, { "value": "SK", "label": "Slovakia" }, { "value": "SI", "label": "Slovenia" }, { "value": "SB", "label": "Solomon Islands" }, { "value": "SO", "label": "Somalia" }, { "value": "ZA", "label": "South Africa" }, { "value": "GS", "label": "South Georgia And The South Sandwich Islands" }, { "value": "KR", "label": "South Korea" }, { "value": "SS", "label": "South Sudan" }, { "value": "ES", "label": "Spain" }, { "value": "LK", "label": "Sri Lanka" }, { "value": "SD", "label": "Sudan" }, { "value": "SR", "label": "Suriname" }, { "value": "SJ", "label": "Svalbard And Jan Mayen" }, { "value": "SE", "label": "Sweden" }, { "value": "CH", "label": "Switzerland" }, { "value": "SY", "label": "Syria" }, { "value": "TW", "label": "Taiwan" }, { "value": "TJ", "label": "Tajikistan" }, { "value": "TZ", "label": "Tanzania" }, { "value": "TH", "label": "Thailand" }, { "value": "TL", "label": "Timor Leste" }, { "value": "TG", "label": "Togo" }, { "value": "TK", "label": "Tokelau" }, { "value": "TO", "label": "Tonga" }, { "value": "TT", "label": "Trinidad And Tobago" }, { "value": "TN", "label": "Tunisia" }, { "value": "TR", "label": "Turkey" }, { "value": "TM", "label": "Turkmenistan" }, { "value": "TC", "label": "Turks And Caicos Islands" }, { "value": "TV", "label": "Tuvalu" }, { "value": "UG", "label": "Uganda" }, { "value": "UA", "label": "Ukraine" }, { "value": "AE", "label": "United Arab Emirates" }, { "value": "GB", "label": "United Kingdom" }, { "value": "US", "label": "United States" }, { "value": "UM", "label": "United States Minor Outlying Islands" }, { "value": "UY", "label": "Uruguay" }, { "value": "VI", "label": "U S Virgin Islands" }, { "value": "UZ", "label": "Uzbekistan" }, { "value": "VU", "label": "Vanuatu" }, { "value": "VA", "label": "Vatican" }, { "value": "VE", "label": "Venezuela" }, { "value": "VN", "label": "Vietnam" }, { "value": "WF", "label": "Wallis And Futuna" }, { "value": "EH", "label": "Western Sahara" }, { "value": "YE", "label": "Yemen" }, { "value": "ZM", "label": "Zambia" }, { "value": "ZW", "label": "Zimbabwe" }]
}
type SectionControls = Omit<Controls, "section">

class Controls {
  private isSectionControl = false;

  private controls: Control<any, WithChooseOptions>[] = [];
  private allControlIds: Set<string> = new Set();

  private add<V>(
    id: string,
    type: string,
    props?: ControlInput<V, WithChooseOptions>
  ) {
    props = props || {}

    if (isEmpty(id)) {
      throw new Error("Control ID cannot be empty")
    }

    id = id.trim()

    // Check for duplicate control ID across all controls
    if (this.allControlIds.has(id)) {
      throw new Error(`A control with the id '${id}' already exists.`)
    }

    this.allControlIds.add(id) // Add the new control ID to the Set

    let label = ensureNotEndsWithDot((props.label || sentenceCase(id))!.trim())

    if (props.hasOwnProperty("placeholder")) {
      // @ts-ignore
      props["placeholder"] = typeof props["placeholder"] === "string" || typeof props["placeholder"] === "number" ? props["placeholder"].toString() : undefined

    }
    // @ts-ignore
    if (!isNullish(props["placeholder"])) {
      // @ts-ignore
      props["placeholder"] = ensureNotEndsWithDot(props["placeholder"]!.trim())
    }
    
    if (!isNullish(props["helpText"])) {
      props["helpText"] = ensureEndsWithDot(props["helpText"]!.trim())
    }
    
    if (!isNullish(props["disabledMessage"])) {
      props["disabledMessage"] = ensureEndsWithDot(props["disabledMessage"]!.trim())
    }
    
    this.raiseTypeValidationErrorMessage(type, props.defaultValue)

    if (type === "checkbox" || type === "switch") {
      if (props.hasOwnProperty("isRequired")) {
        props["isRequired"] = undefined
      }
    }

    const element: Control<V, WithChooseOptions> = {
      ...props,

      id,
      type,
      label,
    }
    if (hasOptions(type) && isNotValidSelectOrChooseValue(element.defaultValue, element)) {
      throw new Error(`Control with ID '${id}' does not have an option with value '${element.defaultValue}'.`)
    }

    this.controls.push(element)
    return this
  }

  section(label: string, defineControls: (section: SectionControls) => void) {
    if (this.isSectionControl) {
      throw new Error(
        `Section control '${label}' cannot be nested within another section control`
      )
    }

    const sectionId = `section-${label.replace(/\s+/g, "_").toLowerCase()}`

    if (this.allControlIds.has(sectionId)) {
      throw new Error(`A section with the id '${sectionId}' already exists.`)
    }

    const sectionControls: SectionControls = new Controls() as SectionControls
    //@ts-ignore
    sectionControls.isSectionControl = true
    //@ts-ignore
    sectionControls.allControlIds = this.allControlIds // Share the Set of all control IDs with the section

    defineControls(sectionControls)

    //@ts-ignore
    if (sectionControls.controls.length) {
      this.add<string>(sectionId, "section", {
        label,
        //@ts-ignore
        controls: sectionControls.controls,
      } as any)

    }

    return this
  }

  addProxySection({
    label = "Proxy Configuration",
    isList = false,
  }: { label?: string; isList?: boolean } = {}) {
    return this.section(label, (section) => {
      if (isList) {
        section.listOfLinks("proxy", {
          label: "Proxies",
          placeholder: "http://your_proxy_address:your_proxy_port",
          isMetadata: true
        })
      } else {
        section.link("proxy", {
          isMetadata: true
        })
      }
    })
  }
  // Each method now requires an 'id' parameter

  text(id: string, props: TextControlInput<string> = {}) {
    return this.add<string>(id, "text", { defaultValue: "", ...props })
  }

  // Method to add a list of text fields
  listOfTexts(id: string, props: TextControlInput<string[]> = {}) {
    const defaultValue = ensureListOfStrings(props.defaultValue || [""], id)

    this.add<string[]>(id, "listOfTexts", {
      ...props,
      defaultValue,
    })

    return this
  }
  number(id: string, props: NumberControlInput<number> = {}) {
    return this.add<number>(id, "number", { defaultValue: null as any, ...props })
  }

  // Method to add a number control that must be greater than or equal to zero
  greaterThanOrEqualToZero(id: string, props: NumberControlInput<number> = {}) {
    // Ensure the minimum value is set to 0
    return this.number(id, { ...props, min: 0 })
  }

  // Method to add a number control that must be greater than or equal to one
  greaterThanOrEqualToOne(id: string, props: NumberControlInput<number> = {}) {
    // Ensure the minimum value is set to 1
    return this.number(id, { ...props, min: 1 })
  }

  switch(id: string, props: Omit<ControlInput<boolean>, "required"> = {}) {
    return this.add<boolean>(id, "switch", { defaultValue: false, ...props })
  }

  checkbox(id: string, props: Omit<ControlInput<boolean>, "required"> = {}) {
    return this.add<boolean>(id, "checkbox", { defaultValue: false, ...props })
  }

  textarea(id: string, props: TextControlInput<string> = {}) {
    return this.add<string>(id, "textarea", { defaultValue: "", ...props })
  }

  link(id: string, props: LinkControlInput<string> = {}) {
    return this.add<string>(id, "link", { defaultValue: "", ...props })
  }

  // Method to add a list of link fields
  listOfLinks(id: string, props: LinkControlInput<string[]> = {}) {
    const defaultValue = ensureListOfStrings(props.defaultValue || [""], id)

    this.add<string[]>(id, "listOfLinks", {
      ...props,
      defaultValue, // Ensure default value is [""] if not provided
    })

    return this
  }
  choose(id: string, props: ControlInput<string, WithChooseOptions> = {}) {
    if (!props.options || !props.options.length) {
      throw new Error(
        `Choose control with id '${id}' requires at least one option`
      )
    }

    return this.add<string>(id, "choose", {
      ...props,
      defaultValue: props.defaultValue ?? null as any,
    })
  }
  select(id: string, props: ControlInput<string, WithOptions> = {}) {
    if (!props.options || !props.options.length) {
      throw new Error(
        `Select control with id  "${id}" requires at least one option`
      )
    }

    return this.add<string>(id, "select", {
      ...props,
      defaultValue: props.defaultValue ?? null as any,
    })
  }


  addLangSelect({
    languages = getDefaultLanguages(),
    label = "Language",
    defaultValue,
  }: { languages?: Option[]; label?: string, defaultValue?: string } = {}) {
    return this.select("lang", {
      defaultValue: defaultValue,
      label, // Use the provided label or the default "Language"
      options: languages, // Use the provided languages array or the defaultLanguages if not provided
    })
  }

  addCountrySelect({
    countries = getDefaultCountries(),
    label = "Country",
    defaultValue,
  }: { countries?: Option[]; label?: string, defaultValue?: string } = {}) {
    return this.select("country", {
      defaultValue: defaultValue,
      label, // Use the provided label or the default "Country"
      options: countries, // Use the provided countries array or getDefaultCountries if not provided
    })
  }

  private defaultData: { [key: string]: any } | null = null; // Cache for default data
  private getDefaultData() {
    // Check if default data is already cached
    if (this.defaultData === null) {
      this.defaultData = {}
      this.iterateControls((control) => {
        //@ts-ignore
        this.defaultData[control.id] =
          control.defaultValue !== undefined ? control.defaultValue : null
      })
    }
    return this.defaultData
  }

  //@ts-ignore
  private getBackendValidationResult(data: any) {
    const defaultData = this.getDefaultData()
    const mergedData: { [key: string]: any } = {}

    // Merge provided data with default data, picking only the keys that correspond to defined controls
    this.iterateControls((control) => {
      const controlId = control.id
      mergedData[controlId] = data.hasOwnProperty(controlId)
        ? data[controlId]
        : defaultData[controlId]
    })

    const errors = this.validate(mergedData) // Validate the merged data

    if (!isEmptyObject(errors)) {
      return {
        data: {},
        metadata: {},
        errors: errors,
      }
    }
    // Split mergedData into data and metadata after validation
    const validatedData: { [key: string]: any } = {}
    const metadata: { [key: string]: any } = {}

    this.iterateControls((control) => {
      const controlId = control.id
      let value = mergedData[controlId]


      if (control.type === "text" || control.type === "textarea") {
        if (canTrim(control)) {
          value = value.trim()
        }
      }
      else if (control.type === "listOfTexts") {

        value = value.filter(isNotEmpty)
        // @ts-ignore
        if (canTrim(control)) {
          value = value.map((x:any) => x.trim())
        }
      }
      // Filter valid URLs for listOfLinks
      else if (control.type === "listOfLinks") {
        value = value.filter(isValidHttpUrl)
      }

      if (control.isMetadata) {
        // Assign to metadata if isMetadata flag is true
        metadata[controlId] = value
      } else {
        // Otherwise, assign to validatedData
        validatedData[controlId] = value
      }
    })

    const result = {
      data: validatedData,
      metadata: metadata,
      errors: errors,
    }

    return result
  }
  private validate(data: any) {
    const validationResults: { [key: string]: string[] } = {} // Stores error messages in an array

    this.iterateControls((control) => {
      const value = data[control.id]
      const { validate, type, id, isShown, isDisabled, isRequired } = control

      let errorMessages: string[] = []

      // Type-specific validation
      const typeValidationErrorMessage = this.getTypeValidationErrorMessage(
        type,
        value
      )

      if (typeValidationErrorMessage) {
        errorMessages.push(typeValidationErrorMessage)
      }



      const isreallyshown = !isShown || !!isShown(data)

      // @ts-ignore
      const isreallydisabled = isFunc(isDisabled) && !!isDisabled(data)

      if (isreallyshown && !isreallydisabled) {
        // Required field check
        if (convertToBool(isRequired, data) && !errorMessages.length) {
          if (isEmpty(value)) {
            errorMessages.push("This field is required.")
          } else if (type === "listOfTexts") {
            // Ensure that the array is not empty for 'listOfTexts' type
            if (!value.length || value.every(isEmpty)) {
              errorMessages.push("This field is required.")
            } else {
              if (!value.some(isNotEmpty)) {
                errorMessages.push("This field must have at least 1 non empty text.")
              }
            }

          } else if (type === "listOfLinks") {
            if (!value.length || value.every(isEmpty)) {
              errorMessages.push("This field is required.")
            } else {
              // Ensure at least one valid URL for 'listOfLinks' type
              if (!value.some(isValidHttpUrl)) {
                errorMessages.push(
                  "This field must have at least 1 valid link. Example: https://example.com/"
                )
              }

            }
          }
        }

        if (
          !errorMessages.length && type === "link" &&
          isNotEmpty(value) &&
          !isValidHttpUrl(value)
        ) {
          errorMessages.push(
            "This field must be a valid URL. Example: https://example.com/"
          )
        }

        if (
          !errorMessages.length && type === "listOfLinks"
        ) {
          const xs = value.filter(isNotEmpty)
          if (xs.length && xs.some((x: string) => !isValidHttpUrl(x))) {
            errorMessages.push(
              "Each non empty field must be a valid URL. Example: https://example.com"
            )
          }
        }

        if (!errorMessages.length && type === "number" && isNotEmpty(value)) {
          const min = (control as any).min
          const max = (control as any).max
          if (isNotEmpty(min) && value < min) {
            errorMessages.push(
              `This field must be greater than or equal to ${min}.`
            )
          }
          if (isNotEmpty(max) && value > max) {
            errorMessages.push(
              `This field must be less than or equal to ${max}.`
            )
          }
        }

        if (hasOptions(type) && !errorMessages.length) {
            // @ts-ignore
            if (isNotValidSelectOrChooseValue(value, control)) {
              errorMessages.push(`"No option value named ${value} exists.`);
            }
        }

        // Custom validation
        if (validate && !errorMessages.length) {
          // Only proceed if no type or required errors
          let validationResult = validate(value, data)

          // Handle string result from validator
          if (
            typeof validationResult === "string" &&
            isNotEmpty(validationResult)
          ) {
            validationResult = validationResult.trim()
            errorMessages.push(
              ensureEndsWithDot(validationResult)
            )
          } else if (Array.isArray(validationResult)) {
            validationResult.forEach((msg) => {
              if (typeof msg === "string" && isNotEmpty(msg)) {
                msg = msg.trim()
                errorMessages.push(ensureEndsWithDot(msg))
              }
            })
          }
        }

      }


      // Assign error messages to validationResults if any
      if (errorMessages.length > 0) {
        validationResults[id] = errorMessages
      }
    })

    return validationResults
  }

  private getTypeValidationErrorMessage(type: string, value: any) {
    switch (type) {
      case "text":
      case "textarea":
      case "link":
        if (typeof value !== "string")
          return "This field must be of type string."
        break
      case "number":
        if (typeof value !== "number" && value !== null)
          return "This field must be of type number or null."
        break
      case "switch":
      case "checkbox":
        if (typeof value !== "boolean")
          return "This field must be of type boolean."
        break
      case "choose":
      case "select":
        if (typeof value !== "string" && value !== null)
          return "This field must be of type string or null."
        break
      case "listOfTexts":
        if (
          !Array.isArray(value) ||
          !value.every((item) => typeof item === "string")
        ) {
          return "This field must be an array of strings."
        }
        break
      case "listOfLinks":
        if (
          !Array.isArray(value) ||
          !value.every((item) => typeof item === "string")
        ) {
          // Assuming all links are strings for simplicity
          return "This field must be an array of strings."
        }
        break
    }
    return
  }

  private raiseTypeValidationErrorMessage(type: string, value: any) {
    const message = this.getTypeValidationErrorMessage(type, value)
    if (message) {
      throw new Error(message)
    }
  }

  private iterateControls(
    callback: (control: Control<any, WithChooseOptions>) => void
  ) {
    this.controls.forEach((control) => {
      if (control.type === "section") {
        (control as any).controls.forEach(callback)
      } else {
        callback(control)
      }
    })
  }
}


function createControls(input_js: string) {
  // Create a new instance of Controls
  const controls = new Controls()

  // Define a function that will accept the 'controls' instance and add controls to it
  const getInputFunc = new Function(
    "controls",
    input_js + "\n return getInput(controls);"
  )

  // Execute the dynamically created function, passing the 'controls' instance
  getInputFunc(controls)

  // Return the modified 'controls' instance with all added controls
  return controls
}


export { Controls, createControls }