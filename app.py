from flask import Flask, render_template_string
import json

app = Flask(__name__)

# We embed the HTML/JS template directly here for a single-file solution.
# In a real project, this would be in a 'templates' folder.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Resume Builder</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Alpine.js (for reactive state management, similar to React but for HTML) -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js"></script>
    
    <!-- html2pdf.js (For direct PDF download) -->
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        /* Custom Scrollbar for Editor */
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #f1f5f9; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

        /* PDF Generation Styles */
        .resume-page {
            width: 210mm;
            min-height: 297mm;
            background: white;
            margin: 0 auto;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        }
        
        @media print {
            body * { visibility: hidden; }
            #resume-preview, #resume-preview * { visibility: visible; }
            #resume-preview { position: absolute; left: 0; top: 0; width: 100%; margin: 0; padding: 0; box-shadow: none; }
        }
    </style>
</head>
<body class="bg-slate-100 text-slate-800 h-screen flex flex-col md:flex-row overflow-hidden" 
      x-data="resumeApp()">

    <!-- LEFT SIDEBAR: EDITOR -->
    <div class="w-full md:w-1/3 lg:w-96 bg-white border-r border-slate-200 h-full flex flex-col shadow-xl z-10">
        
        <!-- Header -->
        <div class="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <h1 class="text-xl font-bold text-slate-800 flex items-center gap-2">
                <i class="fa-solid fa-file-lines text-blue-600"></i> Builder
            </h1>
            <button @click="downloadPDF()" 
                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors shadow-sm">
                <i class="fa-solid fa-download"></i> <span>Download PDF</span>
            </button>
        </div>

        <!-- Tabs -->
        <div class="flex bg-slate-100 p-1 space-x-1">
            <template x-for="tab in tabs" :key="tab.id">
                <button @click="activeTab = tab.id"
                        :class="activeTab === tab.id ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                        class="flex-1 py-2 px-1 rounded-md text-xs font-medium transition-all flex flex-col items-center">
                    <i :class="tab.icon + ' mb-1 text-base'"></i>
                    <span x-text="tab.label"></span>
                </button>
            </template>
        </div>

        <!-- Form Content -->
        <div class="flex-1 overflow-y-auto p-4 custom-scrollbar">
            
            <!-- Template Selector -->
            <div class="mb-6 bg-slate-50 p-3 rounded-lg border border-slate-200">
                <label class="text-xs font-bold text-slate-500 uppercase tracking-wide mb-2 block">Template</label>
                <div class="grid grid-cols-3 gap-2">
                    <button @click="template = 'modern'" :class="template === 'modern' ? 'bg-blue-100 border-blue-400 text-blue-700' : 'bg-white border-slate-200'" class="py-1 px-2 rounded text-xs border font-medium">Modern</button>
                    <button @click="template = 'minimal'" :class="template === 'minimal' ? 'bg-blue-100 border-blue-400 text-blue-700' : 'bg-white border-slate-200'" class="py-1 px-2 rounded text-xs border font-medium">Minimal</button>
                    <button @click="template = 'creative'" :class="template === 'creative' ? 'bg-blue-100 border-blue-400 text-blue-700' : 'bg-white border-slate-200'" class="py-1 px-2 rounded text-xs border font-medium">Creative</button>
                </div>
            </div>

            <!-- PERSONAL TAB -->
            <div x-show="activeTab === 'personal'" class="space-y-3">
                <div class="form-group">
                    <label class="text-xs font-bold text-slate-600">Full Name</label>
                    <input type="text" x-model="data.personal.fullName" class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="form-group">
                    <label class="text-xs font-bold text-slate-600">Email</label>
                    <input type="text" x-model="data.personal.email" class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="form-group">
                    <label class="text-xs font-bold text-slate-600">Phone</label>
                    <input type="text" x-model="data.personal.phone" class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="form-group">
                    <label class="text-xs font-bold text-slate-600">Location</label>
                    <input type="text" x-model="data.personal.location" class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="form-group">
                    <label class="text-xs font-bold text-slate-600">LinkedIn</label>
                    <input type="text" x-model="data.personal.linkedin" class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                 <div class="form-group">
                    <label class="text-xs font-bold text-slate-600">Summary</label>
                    <textarea x-model="data.personal.summary" rows="4" class="w-full border rounded px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"></textarea>
                </div>
            </div>

            <!-- EDUCATION TAB -->
            <div x-show="activeTab === 'education'" class="space-y-4">
                <template x-for="(edu, index) in data.education" :key="edu.id">
                    <div class="bg-slate-50 p-3 rounded border border-slate-200 relative group">
                        <button @click="removeItem('education', edu.id)" class="absolute top-2 right-2 text-slate-400 hover:text-red-500 transition-colors"><i class="fa-solid fa-trash"></i></button>
                        <h3 class="text-xs font-bold text-slate-400 uppercase mb-2">Education <span x-text="index + 1"></span></h3>
                        <input type="text" x-model="edu.school" placeholder="School" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <input type="text" x-model="edu.degree" placeholder="Degree" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <div class="flex gap-2 mb-2">
                            <input type="text" x-model="edu.date" placeholder="Year" class="w-1/2 border rounded px-2 py-1 text-sm">
                            <input type="text" x-model="edu.gpa" placeholder="GPA" class="w-1/2 border rounded px-2 py-1 text-sm">
                        </div>
                        <textarea x-model="edu.details" placeholder="Details" class="w-full border rounded px-2 py-1 text-sm"></textarea>
                    </div>
                </template>
                <button @click="addItem('education')" class="w-full py-2 border-2 border-dashed border-slate-300 rounded text-slate-500 hover:border-blue-500 hover:text-blue-500 text-sm font-medium transition-colors">
                    <i class="fa-solid fa-plus mr-1"></i> Add Education
                </button>
            </div>

            <!-- EXPERIENCE TAB -->
            <div x-show="activeTab === 'experience'" class="space-y-4">
                 <template x-for="(exp, index) in data.experience" :key="exp.id">
                    <div class="bg-slate-50 p-3 rounded border border-slate-200 relative group">
                        <button @click="removeItem('experience', exp.id)" class="absolute top-2 right-2 text-slate-400 hover:text-red-500 transition-colors"><i class="fa-solid fa-trash"></i></button>
                        <h3 class="text-xs font-bold text-slate-400 uppercase mb-2">Job <span x-text="index + 1"></span></h3>
                        <input type="text" x-model="exp.company" placeholder="Company" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <input type="text" x-model="exp.role" placeholder="Role" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <div class="flex gap-2 mb-2">
                            <input type="text" x-model="exp.location" placeholder="Location" class="w-1/2 border rounded px-2 py-1 text-sm">
                            <input type="text" x-model="exp.date" placeholder="Date" class="w-1/2 border rounded px-2 py-1 text-sm">
                        </div>
                        <textarea x-model="exp.details" placeholder="Responsibilities" rows="3" class="w-full border rounded px-2 py-1 text-sm"></textarea>
                    </div>
                </template>
                <button @click="addItem('experience')" class="w-full py-2 border-2 border-dashed border-slate-300 rounded text-slate-500 hover:border-blue-500 hover:text-blue-500 text-sm font-medium transition-colors">
                    <i class="fa-solid fa-plus mr-1"></i> Add Experience
                </button>
            </div>

            <!-- PROJECTS TAB -->
            <div x-show="activeTab === 'projects'" class="space-y-4">
                 <template x-for="(proj, index) in data.projects" :key="proj.id">
                    <div class="bg-slate-50 p-3 rounded border border-slate-200 relative group">
                        <button @click="removeItem('projects', proj.id)" class="absolute top-2 right-2 text-slate-400 hover:text-red-500 transition-colors"><i class="fa-solid fa-trash"></i></button>
                        <h3 class="text-xs font-bold text-slate-400 uppercase mb-2">Project <span x-text="index + 1"></span></h3>
                        <input type="text" x-model="proj.name" placeholder="Project Name" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <input type="text" x-model="proj.technologies" placeholder="Tech Stack" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <input type="text" x-model="proj.link" placeholder="Link" class="w-full border rounded px-2 py-1 text-sm mb-2">
                        <textarea x-model="proj.details" placeholder="Description" rows="2" class="w-full border rounded px-2 py-1 text-sm"></textarea>
                    </div>
                </template>
                <button @click="addItem('projects')" class="w-full py-2 border-2 border-dashed border-slate-300 rounded text-slate-500 hover:border-blue-500 hover:text-blue-500 text-sm font-medium transition-colors">
                    <i class="fa-solid fa-plus mr-1"></i> Add Project
                </button>
            </div>

            <!-- SKILLS TAB -->
             <div x-show="activeTab === 'skills'" class="space-y-2">
                <template x-for="(skill, index) in data.skills" :key="index">
                    <div class="flex gap-2">
                        <input type="text" x-model="data.skills[index]" class="flex-1 border rounded px-2 py-2 text-sm">
                        <button @click="removeSkill(index)" class="text-slate-400 hover:text-red-500"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </template>
                <button @click="addSkill()" class="w-full py-2 mt-2 border-2 border-dashed border-slate-300 rounded text-slate-500 hover:border-blue-500 hover:text-blue-500 text-sm font-medium transition-colors">
                    <i class="fa-solid fa-plus mr-1"></i> Add Skill
                </button>
            </div>

        </div>
    </div>

    <!-- RIGHT SIDEBAR: PREVIEW -->
    <div class="flex-1 bg-slate-200 p-8 overflow-y-auto flex justify-center">
        
        <!-- RESUME CONTAINER (This is what gets printed) -->
        <div id="resume-preview" class="resume-page p-8 transition-all duration-300 ease-in-out">
            
            <!-- --- MODERN TEMPLATE --- -->
            <div x-show="template === 'modern'" class="h-full w-full font-sans text-slate-800">
                <header class="border-b-2 border-slate-800 pb-6 mb-6">
                    <h1 class="text-4xl font-bold uppercase tracking-wide text-slate-900 mb-2" x-text="data.personal.fullName"></h1>
                    <div class="flex flex-wrap gap-4 text-sm text-slate-600">
                        <span x-show="data.personal.email" class="flex items-center gap-1"><i class="fa-solid fa-envelope"></i> <span x-text="data.personal.email"></span></span>
                        <span x-show="data.personal.phone" class="flex items-center gap-1"><i class="fa-solid fa-phone"></i> <span x-text="data.personal.phone"></span></span>
                        <span x-show="data.personal.location" class="flex items-center gap-1"><i class="fa-solid fa-map-pin"></i> <span x-text="data.personal.location"></span></span>
                        <span x-show="data.personal.linkedin" class="flex items-center gap-1"><i class="fa-brands fa-linkedin"></i> <span x-text="data.personal.linkedin"></span></span>
                    </div>
                </header>
                <div class="grid grid-cols-3 gap-8">
                    <div class="col-span-2 space-y-6">
                        <section x-show="data.personal.summary">
                            <h2 class="text-xl font-bold uppercase border-b border-slate-300 mb-3 pb-1">Summary</h2>
                            <p class="text-sm leading-relaxed text-slate-700" x-text="data.personal.summary"></p>
                        </section>
                        <section>
                            <h2 class="text-xl font-bold uppercase border-b border-slate-300 mb-3 pb-1">Education</h2>
                            <template x-for="edu in data.education" :key="edu.id">
                                <div class="mb-4">
                                    <div class="flex justify-between items-baseline mb-1">
                                        <h3 class="font-bold text-lg" x-text="edu.school"></h3>
                                        <span class="text-sm italic" x-text="edu.date"></span>
                                    </div>
                                    <div class="flex justify-between items-baseline mb-1 text-slate-700">
                                        <span class="font-medium" x-text="edu.degree"></span>
                                        <span class="text-sm" x-text="edu.location"></span>
                                    </div>
                                    <p class="text-sm text-slate-600 mb-1">GPA: <span x-text="edu.gpa"></span></p>
                                    <p class="text-sm text-slate-600" x-text="edu.details"></p>
                                </div>
                            </template>
                        </section>
                        <section>
                            <h2 class="text-xl font-bold uppercase border-b border-slate-300 mb-3 pb-1">Experience</h2>
                            <template x-for="exp in data.experience" :key="exp.id">
                                <div class="mb-4">
                                    <div class="flex justify-between items-baseline mb-1">
                                        <h3 class="font-bold text-lg" x-text="exp.company"></h3>
                                        <span class="text-sm italic" x-text="exp.date"></span>
                                    </div>
                                    <div class="text-sm text-slate-700 font-medium mb-1" x-text="exp.role"></div>
                                    <div class="text-sm text-slate-600 whitespace-pre-line border-l-2 border-slate-200 pl-2" x-text="exp.details"></div>
                                </div>
                            </template>
                        </section>
                    </div>
                    <div class="col-span-1 space-y-6">
                        <section>
                            <h2 class="text-xl font-bold uppercase border-b border-slate-300 mb-3 pb-1">Skills</h2>
                            <div class="flex flex-wrap gap-2">
                                <template x-for="skill in data.skills">
                                    <span class="bg-slate-100 text-slate-800 px-2 py-1 rounded text-xs font-semibold" x-text="skill"></span>
                                </template>
                            </div>
                        </section>
                        <section>
                            <h2 class="text-xl font-bold uppercase border-b border-slate-300 mb-3 pb-1">Projects</h2>
                            <template x-for="proj in data.projects" :key="proj.id">
                                <div class="mb-4">
                                    <h3 class="font-bold text-md" x-text="proj.name"></h3>
                                    <p class="text-xs text-blue-600 mb-1" x-text="proj.technologies"></p>
                                    <p class="text-xs text-slate-600 leading-snug" x-text="proj.details"></p>
                                </div>
                            </template>
                        </section>
                    </div>
                </div>
            </div>

            <!-- --- MINIMAL TEMPLATE --- -->
            <div x-show="template === 'minimal'" class="h-full w-full font-serif text-gray-900">
                <header class="text-center mb-8">
                    <h1 class="text-3xl font-normal mb-2 tracking-widest uppercase" x-text="data.personal.fullName"></h1>
                    <div class="text-sm text-gray-600 flex justify-center gap-4 flex-wrap">
                        <span x-text="data.personal.email"></span> • <span x-text="data.personal.phone"></span>
                    </div>
                </header>
                <div class="space-y-6">
                    <section x-show="data.personal.summary">
                        <p class="text-sm leading-relaxed text-center max-w-2xl mx-auto italic text-gray-700" x-text="data.personal.summary"></p>
                    </section>
                    <section>
                        <h2 class="text-sm font-bold uppercase tracking-widest border-b border-gray-900 mb-4 pb-1">Education</h2>
                        <template x-for="edu in data.education" :key="edu.id">
                            <div class="mb-4 grid grid-cols-4 gap-4">
                                <div class="col-span-1 text-sm text-gray-600" x-text="edu.date"></div>
                                <div class="col-span-3">
                                    <h3 class="font-bold" x-text="edu.school"></h3>
                                    <div class="text-sm italic mb-1" x-text="edu.degree"></div>
                                    <div class="text-sm text-gray-700" x-text="edu.details"></div>
                                </div>
                            </div>
                        </template>
                    </section>
                     <section>
                        <h2 class="text-sm font-bold uppercase tracking-widest border-b border-gray-900 mb-4 pb-1">Experience</h2>
                        <template x-for="exp in data.experience" :key="exp.id">
                            <div class="mb-4 grid grid-cols-4 gap-4">
                                <div class="col-span-1 text-sm text-gray-600">
                                    <div x-text="exp.date"></div>
                                    <div class="italic" x-text="exp.location"></div>
                                </div>
                                <div class="col-span-3">
                                    <h3 class="font-bold" x-text="exp.company"></h3>
                                    <div class="text-sm italic mb-2 text-blue-900" x-text="exp.role"></div>
                                    <div class="text-sm text-gray-700 whitespace-pre-line" x-text="exp.details"></div>
                                </div>
                            </div>
                        </template>
                    </section>
                    <section>
                         <h2 class="text-sm font-bold uppercase tracking-widest border-b border-gray-900 mb-4 pb-1">Projects & Skills</h2>
                         <div class="text-sm text-gray-700 mb-4">
                             <span class="font-bold text-gray-900">Skills: </span>
                             <span x-text="data.skills.join(' • ')"></span>
                         </div>
                         <template x-for="proj in data.projects" :key="proj.id">
                             <div class="mb-3">
                                 <div class="text-sm font-bold text-gray-800" x-text="proj.name"></div>
                                 <div class="text-sm italic text-gray-500 mb-1" x-text="proj.technologies"></div>
                                 <div class="text-sm text-gray-700" x-text="proj.details"></div>
                             </div>
                         </template>
                    </section>
                </div>
            </div>

            <!-- --- CREATIVE TEMPLATE --- -->
            <div x-show="template === 'creative'" class="h-full w-full flex text-slate-800 font-sans">
                <div class="w-1/3 bg-slate-900 text-white p-6 flex flex-col gap-6">
                    <div class="text-center">
                        <div class="w-20 h-20 bg-blue-500 rounded-full mx-auto mb-3 flex items-center justify-center text-2xl font-bold" x-text="data.personal.fullName.charAt(0)"></div>
                        <h1 class="text-xl font-bold leading-tight" x-text="data.personal.fullName"></h1>
                        <p class="text-blue-300 text-xs mt-2" x-text="data.personal.email"></p>
                    </div>
                    <div>
                        <h3 class="uppercase tracking-widest text-xs font-bold text-blue-400 border-b border-slate-700 pb-2 mb-2">Skills</h3>
                        <div class="flex flex-wrap gap-2">
                             <template x-for="skill in data.skills">
                                <span class="text-xs bg-slate-800 px-2 py-1 rounded text-slate-300 border border-slate-700" x-text="skill"></span>
                            </template>
                        </div>
                    </div>
                     <div>
                        <h3 class="uppercase tracking-widest text-xs font-bold text-blue-400 border-b border-slate-700 pb-2 mb-2">Education</h3>
                         <template x-for="edu in data.education" :key="edu.id">
                            <div class="text-sm mb-3">
                                <div class="font-bold text-white" x-text="edu.school"></div>
                                <div class="text-blue-300 text-xs" x-text="edu.degree"></div>
                                <div class="text-slate-500 text-xs">GPA: <span x-text="edu.gpa"></span></div>
                            </div>
                        </template>
                    </div>
                </div>
                <div class="w-2/3 p-6 bg-slate-50">
                    <div class="mb-6">
                        <h2 class="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <i class="fa-solid fa-user text-blue-600"></i> Profile
                        </h2>
                        <p class="text-sm text-slate-600" x-text="data.personal.summary"></p>
                    </div>
                    <div class="mb-6">
                        <h2 class="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <i class="fa-solid fa-briefcase text-blue-600"></i> Experience
                        </h2>
                        <template x-for="exp in data.experience" :key="exp.id">
                            <div class="mb-4 relative pl-4 border-l-2 border-blue-200">
                                <div class="font-bold text-slate-800" x-text="exp.role"></div>
                                <div class="text-xs text-blue-600 font-medium mb-1"><span x-text="exp.company"></span> | <span x-text="exp.date"></span></div>
                                <div class="text-sm text-slate-600 whitespace-pre-line" x-text="exp.details"></div>
                            </div>
                        </template>
                    </div>
                     <div>
                        <h2 class="text-xl font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <i class="fa-solid fa-code text-blue-600"></i> Projects
                        </h2>
                        <div class="space-y-3">
                             <template x-for="proj in data.projects" :key="proj.id">
                                <div class="bg-white p-3 rounded shadow-sm border border-slate-100">
                                    <div class="font-bold text-slate-800" x-text="proj.name"></div>
                                    <div class="text-xs text-blue-500 font-semibold mb-1" x-text="proj.technologies"></div>
                                    <div class="text-sm text-slate-600" x-text="proj.details"></div>
                                </div>
                            </template>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- Application Logic -->
    <script>
        document.addEventListener('alpine:init', () => {
            Alpine.data('resumeApp', () => ({
                activeTab: 'personal',
                template: 'modern',
                tabs: [
                    { id: 'personal', icon: 'fa-solid fa-user', label: 'Bio' },
                    { id: 'education', icon: 'fa-solid fa-graduation-cap', label: 'Edu' },
                    { id: 'experience', icon: 'fa-solid fa-briefcase', label: 'Exp' },
                    { id: 'projects', icon: 'fa-solid fa-code', label: 'Proj' },
                    { id: 'skills', icon: 'fa-solid fa-award', label: 'Skill' },
                ],
                data: {
                    personal: {
                        fullName: "Alex Chen",
                        email: "alex.chen@univ.edu",
                        phone: "(555) 123-4567",
                        location: "San Francisco, CA",
                        linkedin: "linkedin.com/in/alex",
                        summary: "CS Senior seeking full stack roles. Passionate about React, Python, and scalable systems."
                    },
                    education: [
                        { id: 1, school: "Tech University", degree: "B.S. Computer Science", date: "2025", gpa: "3.8", details: "Data Structures, Algorithms" }
                    ],
                    experience: [
                        { id: 1, company: "StartUp Inc", role: "Intern", location: "Remote", date: "Summer 2024", details: "Built React dashboard. Optimized API calls." }
                    ],
                    projects: [
                        { id: 1, name: "Task App", technologies: "React, Firebase", link: "github.com", details: "Real-time task manager with drag and drop." }
                    ],
                    skills: ["Python", "JavaScript", "React", "Flask", "SQL"]
                },
                
                addItem(section) {
                    const id = Date.now();
                    const items = {
                        education: { id, school: "New School", degree: "", date: "", gpa: "", details: "" },
                        experience: { id, company: "New Company", role: "", location: "", date: "", details: "" },
                        projects: { id, name: "New Project", technologies: "", link: "", details: "" }
                    };
                    this.data[section].push(items[section]);
                },
                
                removeItem(section, id) {
                    this.data[section] = this.data[section].filter(i => i.id !== id);
                },

                addSkill() {
                    this.data.skills.push("New Skill");
                },

                removeSkill(index) {
                    this.data.skills = this.data.skills.filter((_, i) => i !== index);
                },

                downloadPDF() {
                    const element = document.getElementById('resume-preview');
                    const opt = {
                        margin: 0,
                        filename: 'Resume.pdf',
                        image: { type: 'jpeg', quality: 0.98 },
                        html2canvas: { scale: 2 },
                        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                    };
                    
                    // Show loading state could be added here
                    html2pdf().set(opt).from(element).save();
                }
            }));
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)

