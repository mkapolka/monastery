require 'monastery/templates/template.rb'

module Templates
    class Template
        class << self
            alias_method :material, :mixin
        end
    end

    class Material < UniqueSubtemplate
        self.container_property = Properties::Material
    end

    class Metal < Material
        #self.properties += [Hard, Conductive]
        self.properties = [Hard]
    end

    class Porcelain < Material
        self.properties = [Hard, Brittle]
    end
end
