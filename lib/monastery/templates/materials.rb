require 'monastery/templates/template.rb'

module Templates
    class Material < UniqueSubtemplate
        self.container_property = Properties::Material
    end

    class Metal < Material
        #self.properties += [Hard, Conductive]
        self.properties = [Hard]
    end

    class Porcelain < Material
        #self.properties += [Hard, Brittle]
        self.properties = [Hard]
    end
end
