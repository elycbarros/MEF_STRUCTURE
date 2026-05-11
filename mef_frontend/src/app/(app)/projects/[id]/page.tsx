import { Button, buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { ArrowLeft, Play, Layout, FileText, Share2 } from "lucide-react";
import Link from "next/link";

export default function ProjectDetailsPage({ params }: { params: { id: string } }) {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/projects"
            className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "rounded-full")}
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Projeto {params.id}</h1>
            <p className="text-muted-foreground">Ambiente de Análise e Edição</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Share2 className="w-4 h-4 mr-2" />
            Compartilhar
          </Button>
          <Button className="bg-macos-blue hover:bg-macos-blue/90">
            <Play className="w-4 h-4 mr-2" />
            Executar Análise
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
        <div className="lg:col-span-2 bg-muted/30 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center text-muted-foreground p-12 text-center">
          <Layout className="w-12 h-12 mb-4 opacity-20" />
          <h3 className="text-xl font-medium text-foreground">Visualizador 3D</h3>
          <p className="max-w-xs mt-2">O motor Three.js será inicializado nesta área para renderização do modelo estrutural.</p>
        </div>
        
        <div className="space-y-6">
          <div className="bg-card rounded-2xl border p-6 space-y-4">
            <div className="flex items-center gap-2 font-semibold">
              <FileText className="w-4 h-4 text-macos-blue" />
              Resumo do Modelo
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Pavimentos:</span>
                <span className="font-medium">10</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Nós:</span>
                <span className="font-medium">124</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Membros:</span>
                <span className="font-medium">248</span>
              </div>
            </div>
          </div>
          
          <div className="bg-macos-blue/5 rounded-2xl border border-macos-blue/20 p-6 text-center">
            <p className="text-sm text-macos-blue font-medium italic">Pronto para análise linear de 1ª ordem e P-Delta.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
