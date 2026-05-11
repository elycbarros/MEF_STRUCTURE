import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button, buttonVariants } from "@/components/ui/button";
import { Plus, Folder, Calendar, ArrowRight } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const mockProjects = [
  { id: "1", name: "Edifício 10 andares", type: "Pórtico 3D", createdAt: "2025-01-15", status: "Estável" },
  { id: "2", name: "Galpão Industrial", type: "Treliça", createdAt: "2025-02-20", status: "Em Análise" },
  { id: "3", name: "Ponte Estaiada v2", type: "Infraestrutura", createdAt: "2025-03-05", status: "Aprovado" },
];

export default function ProjectsPage() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Meus Projetos</h1>
          <p className="text-muted-foreground">Gerencie e analise seus modelos estruturais.</p>
        </div>
        <Button className="bg-macos-blue hover:bg-macos-blue/90 shadow-lg shadow-macos-blue/20">
          <Plus className="w-4 h-4 mr-2" />
          Novo Projeto
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockProjects.map((project) => (
          <Card key={project.id} className="group hover:border-macos-blue/50 transition-all duration-300 shadow-sm hover:shadow-md">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="p-2 bg-macos-blue/10 rounded-lg">
                  <Folder className="w-5 h-5 text-macos-blue" />
                </div>
                <span className={cn(
                  "text-[10px] uppercase font-bold px-2 py-1 rounded-full",
                  project.status === "Estável" ? "bg-green-500/10 text-green-600" : 
                  project.status === "Aprovado" ? "bg-blue-500/10 text-blue-600" : "bg-orange-500/10 text-orange-600"
                )}>
                  {project.status}
                </span>
              </div>
              <CardTitle className="mt-4 text-lg">{project.name}</CardTitle>
              <CardDescription>{project.type}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center text-xs text-muted-foreground gap-4">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {project.createdAt}
                </div>
              </div>
              <Link
                href={`/projects/${project.id}`}
                className={cn(
                  buttonVariants({ variant: "ghost" }),
                  "w-full mt-6 group-hover:bg-macos-blue group-hover:text-white transition-all"
                )}
              >
                Abrir Projeto
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
