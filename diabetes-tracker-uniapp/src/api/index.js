const BASE = '/api'

function showLogin() {
  // TODO: 登录弹窗
  console.warn('需要登录')
}

async function request(method, path, body = null) {
  const opts = { method }
  if (body) {
    opts.headers = { 'Content-Type': 'application/json' }
    opts.body = JSON.stringify(body)
  }
  const r = await fetch(BASE + path, opts)
  if (r.status === 401) showLogin()
  return r
}

// ---- Profile ----
export function getProfile()   { return request('GET', '/profile').then(r => r.json()) }
export function updateProfile(d){ return request('POST', '/profile', d).then(r => r.json()) }

// ---- Diet ----
export function listDiet()     { return request('GET', '/diet').then(r => r.json()) }
export function addDiet(d)     { return request('POST', '/diet', d).then(r => r.json()) }
export function updateDiet(id, d) { return request('PUT', `/diet/${id}`, d).then(r => r.json()) }
export function deleteDiet(id) { return request('DELETE', `/diet/${id}`).then(r => r.json()) }

// ---- Exercise ----
export function listExercise()     { return request('GET', '/exercise').then(r => r.json()) }
export function addExercise(d)     { return request('POST', '/exercise', d).then(r => r.json()) }
export function updateExercise(id, d) { return request('PUT', `/exercise/${id}`, d).then(r => r.json()) }
export function deleteExercise(id) { return request('DELETE', `/exercise/${id}`).then(r => r.json()) }

// ---- Glucose ----
export function listGlucose()     { return request('GET', '/glucose').then(r => r.json()) }
export function addGlucose(d)     { return request('POST', '/glucose', d).then(r => r.json()) }
export function updateGlucose(id, d) { return request('PUT', `/glucose/${id}`, d).then(r => r.json()) }
export function deleteGlucose(id) { return request('DELETE', `/glucose/${id}`).then(r => r.json()) }

// ---- Medication ----
export function listMedication()     { return request('GET', '/medication').then(r => r.json()) }
export function addMedication(d)     { return request('POST', '/medication', d).then(r => r.json()) }
export function updateMedication(id, d) { return request('PUT', `/medication/${id}`, d).then(r => r.json()) }
export function deleteMedication(id) { return request('DELETE', `/medication/${id}`).then(r => r.json()) }

// ---- Followup ----
export function listFollowup()     { return request('GET', '/followup').then(r => r.json()) }
export function addFollowup(d)     { return request('POST', '/followup', d).then(r => r.json()) }
export function updateFollowup(id, d) { return request('PUT', `/followup/${id}`, d).then(r => r.json()) }
export function deleteFollowup(id) { return request('DELETE', `/followup/${id}`).then(r => r.json()) }

// ---- Goals ----
export function getGoals()     { return request('GET', '/goals').then(r => r.json()) }
export function updateGoals(d) { return request('POST', '/goals', d).then(r => r.json()) }

// ---- Custom Drugs ----
export function listCustomDrugs()     { return request('GET', '/custom-drugs').then(r => r.json()) }
export function addCustomDrug(d)      { return request('POST', '/custom-drugs', d).then(r => r.json()) }
export function deleteCustomDrug(id)  { return request('DELETE', `/custom-drugs/${id}`).then(r => r.json()) }

// ---- Meal Templates ----
export function listMealTemplates()     { return request('GET', '/meal-templates').then(r => r.json()) }
export function addMealTemplate(d)      { return request('POST', '/meal-templates', d).then(r => r.json()) }
export function updateMealTemplate(id, d){ return request('PUT', `/meal-templates/${id}`, d).then(r => r.json()) }
export function deleteMealTemplate(id)  { return request('DELETE', `/meal-templates/${id}`).then(r => r.json()) }

// ---- Members ----
export function listMembers()       { return request('GET', '/members').then(r => r.json()) }
export function addMember(d)        { return request('POST', '/members', d).then(r => r.json()) }
export function updateMember(id, d) { return request('PUT', `/members/${id}`, d).then(r => r.json()) }
export function deleteMember(id)    { return request('DELETE', `/members/${id}`).then(r => r.json()) }
export function switchMember(uid)   { return request('POST', '/members/switch', { user_id: uid }).then(r => r.json()) }
export function getCurrentMember()  { return request('GET', '/members/current').then(r => r.json()) }

// ---- Auth ----
export function authStatus() { return request('GET', '/auth-status').then(r => r.json()) }
export function login(pwd)   { return request('POST', '/login', { password: pwd }).then(r => r.json()) }
export function logout()     { return request('POST', '/logout').then(r => r.json()) }

// ---- Backup ----
export function backup()  { return request('GET', '/backup').then(r => r.json()) }
export function restore(d) { return request('POST', '/restore', d).then(r => r.json()) }
