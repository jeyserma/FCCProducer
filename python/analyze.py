
import glob
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.EnableImplicitMT(1)

ROOT.gSystem.Load("libedm4hep")
ROOT.gSystem.Load("libpodio")
ROOT.gSystem.Load("libFCCAnalyses")
ROOT.gErrorIgnoreLevel = ROOT.kFatal
_edm  = ROOT.edm4hep.ReconstructedParticleData()
_pod  = ROOT.podio.ObjectID()
_fcc  = ROOT.dummyLoader





ROOT.gInterpreter.Declare("""

using Vec_b = ROOT::VecOps::RVec<bool>;
using Vec_d = ROOT::VecOps::RVec<double>;
using Vec_f = ROOT::VecOps::RVec<float>;
using Vec_i = ROOT::VecOps::RVec<int>;
using Vec_ui = ROOT::VecOps::RVec<unsigned int>;

using rp = edm4hep::ReconstructedParticleData;
using Vec_rp = ROOT::VecOps::RVec<edm4hep::ReconstructedParticleData>;
using Vec_mc = ROOT::VecOps::RVec<edm4hep::MCParticleData>;
using Vec_tlv = ROOT::VecOps::RVec<TLorentzVector>;
    

Vec_i get_gen_pdg__(Vec_mc mc, int pdgId, bool abs=true, bool stable=true) {
   Vec_i result;
   //std::cout << "ddddddddd" << std::endl;
   for(size_t i = 0; i < mc.size(); ++i) {
        auto & p = mc[i];
        if(!((abs and std::abs(p.PDG) == pdgId) or (not abs and p.PDG == pdgId))) continue;
        //cout << p.PDG << endl;
        if(stable && p.generatorStatus != 1) continue;
        result.push_back(i);






        //if((abs and std::abs(p.PDG) == pdgId) or (not abs and p.PDG == pdgId)) result.emplace_back(p);
   }
   return result;
}



Vec_i test_(Vec_mc mc, int pdgId, bool abs=true, bool stable=true) {
   Vec_i result;
   std::cout << "ddddddddd" << std::endl;
   for(size_t i = 0; i < mc.size(); ++i) {
        auto & p = mc[i];
        if(!((abs and std::abs(p.PDG) == pdgId) or (not abs and p.PDG == pdgId))) continue;
        cout << p.PDG << endl;
        if(stable && p.generatorStatus != 1) continue;
        result.push_back(i);






        //if((abs and std::abs(p.PDG) == pdgId) or (not abs and p.PDG == pdgId)) result.emplace_back(p);
   }
   return result;
}


bool myFilter(ROOT::VecOps::RVec<float> mass) {
    for (size_t i = 0; i < mass.size(); ++i) {
        if (mass.at(i)>80. && mass.at(i)<100.)
            return true;
    }
    return false;
}
""")

def make_df(dIn):
    fIns = glob.glob(f"{dIn}/*.root")
    names = ROOT.std.vector('string')()
    for n in fIns: names.push_back(n)
    df = ROOT.RDataFrame("events", names)

    df = df.Define("mc_stable", "FCCAnalyses::MCParticle::sel_genStatus(1)(Particle)")
    df = df.Define("mc_theta", "FCCAnalyses::MCParticle::get_theta(mc_stable)")
    
    df = df.Define("quarks_gen_minus", "get_gen_pdg__(Particle, -2, false, false)")
    #df = df.Define("quarks_gen", "cout << quarks_gen_.size() << endl; return quarks_gen_")
    df = df.Define("mc_theta_minus", "mc_theta[quarks_gen_minus[0]]")
    
    df = df.Define("quarks_gen_plus", "get_gen_pdg__(Particle, 2, false, false)")
    #df = df.Define("quarks_gen", "cout << quarks_gen_.size() << endl; return quarks_gen_")
    df = df.Define("mc_theta_plus", "mc_theta[quarks_gen_plus[0]]")
    
    
    df = df.Define("test", "test_(Particle, -2, false, false)")
    return df

def main():

    df_kkmcee = make_df("/eos/experiment/fcc/users/j/jaeyserm/sampleProduction2024/winter2023/IDEA/kkmcee_ee_uu_noISR_noBES_ecm91p2")
    df_p8 = make_df("/eos/experiment/fcc/users/j/jaeyserm/sampleProduction2024/winter2023/IDEA/p8_ee_uu_noISR_noBES_ecm91p2")
    df_wz3p8 = make_df("/eos/experiment/fcc/users/j/jaeyserm/sampleProduction2024/winter2023/IDEA/wz3p8_ee_uu_noISR_noBES_ecm91p2")

    mc_theta_kkmcee = df_kkmcee.Histo1D(("mc_theta_kkmcee", "", 400, 0, 4), "mc_theta")
    mc_theta_p8 = df_p8.Histo1D(("mc_theta_p8", "", 400, 0, 4), "mc_theta")
    mc_theta_wz3p8 = df_wz3p8.Histo1D(("mc_theta_wz3p8", "", 400, 0, 4), "mc_theta")
    
    mc_theta_kkmcee_plus = df_kkmcee.Histo1D(("mc_theta_kkmcee_plus", "", 400, 0, 4), "mc_theta_plus")
    mc_theta_p8_plus = df_p8.Histo1D(("mc_theta_p8_plus", "", 400, 0, 4), "mc_theta_plus")
    mc_theta_wz3p8_plus = df_wz3p8.Histo1D(("mc_theta_wz3p8_plus", "", 400, 0, 4), "mc_theta_plus")
    
    mc_theta_kkmcee_minus = df_kkmcee.Histo1D(("mc_theta_kkmcee_minus", "", 400, 0, 4), "mc_theta_minus")
    mc_theta_p8_minus = df_p8.Histo1D(("mc_theta_p8_minus", "", 400, 0, 4), "mc_theta_minus")
    mc_theta_wz3p8_minus = df_wz3p8.Histo1D(("mc_theta_wz3p8_minus", "", 400, 0, 4), "mc_theta_minus")
    
    test = df_wz3p8.Histo1D(("quarks_gen", "", 400, 0, 4), "test")

    ROOT.ROOT.RDF.RunGraphs([mc_theta_kkmcee, mc_theta_p8, mc_theta_wz3p8, mc_theta_kkmcee_plus, mc_theta_p8_plus, mc_theta_wz3p8_plus, mc_theta_kkmcee_minus, mc_theta_p8_minus, mc_theta_wz3p8_minus, test])


    canvas = ROOT.TCanvas("", "")
    mc_theta_kkmcee.GetXaxis().SetTitle("#theta (rad)")
    mc_theta_kkmcee.GetYaxis().SetTitle("Events")
    mc_theta_kkmcee.SetLineColor(ROOT.kBlue)
    mc_theta_kkmcee.SetLineWidth(2)
    mc_theta_kkmcee.Draw()
    mc_theta_p8.SetLineColor(ROOT.kRed)
    mc_theta_p8.SetLineWidth(2)
    mc_theta_p8.Draw("SAME")
    mc_theta_wz3p8.SetLineColor(ROOT.kBlack)
    mc_theta_wz3p8.SetLineWidth(2)
    mc_theta_wz3p8.Draw("SAME")

    legend = ROOT.TLegend(0.6, 0.6, 0.8, 0.8)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.AddEntry("mc_theta_kkmcee", "KKMCee", "L")
    legend.AddEntry("mc_theta_p8", "Pythia8", "L")
    legend.Draw()
    canvas.SaveAs("/eos/user/j/jaeyserm/www/fccee/mc_theta.png")
    
    

    canvas = ROOT.TCanvas("", "")
    mc_theta_kkmcee_minus.GetXaxis().SetTitle("#theta (rad)")
    mc_theta_kkmcee_minus.GetYaxis().SetTitle("Events")
    mc_theta_kkmcee_minus.SetLineColor(ROOT.kBlue)
    mc_theta_kkmcee_minus.SetLineWidth(2)
    mc_theta_kkmcee_minus.Draw()
    mc_theta_p8_minus.SetLineColor(ROOT.kRed)
    mc_theta_p8_minus.SetLineWidth(2)
    mc_theta_p8_minus.Draw("SAME")
    mc_theta_wz3p8_minus.SetLineColor(ROOT.kBlack)
    mc_theta_wz3p8_minus.SetLineWidth(2)
    mc_theta_wz3p8_minus.Draw("SAME")

    legend = ROOT.TLegend(0.6, 0.6, 0.8, 0.8)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.AddEntry("mc_theta_kkmcee_minus", "KKMCee", "L")
    legend.AddEntry("mc_theta_p8_minus", "Pythia8", "L")
    legend.Draw()
    canvas.SaveAs("/eos/user/j/jaeyserm/www/fccee/mc_theta_minus.png")
    
    
    canvas = ROOT.TCanvas("", "")
    mc_theta_kkmcee_plus.GetXaxis().SetTitle("#theta (rad)")
    mc_theta_kkmcee_plus.GetYaxis().SetTitle("Events")
    mc_theta_kkmcee_plus.SetLineColor(ROOT.kBlue)
    mc_theta_kkmcee_plus.SetLineWidth(2)
    mc_theta_kkmcee_plus.Draw()
    mc_theta_p8_plus.SetLineColor(ROOT.kRed)
    mc_theta_p8_plus.SetLineWidth(2)
    mc_theta_p8_plus.Draw("SAME")
    mc_theta_wz3p8_plus.SetLineColor(ROOT.kBlack)
    mc_theta_wz3p8_plus.SetLineWidth(2)
    mc_theta_wz3p8_plus.Draw("SAME")

    legend = ROOT.TLegend(0.6, 0.6, 0.8, 0.8)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.AddEntry("mc_theta_kkmcee_plus", "KKMCee", "L")
    legend.AddEntry("mc_theta_p8_plus", "Pythia8", "L")
    legend.Draw()
    canvas.SaveAs("/eos/user/j/jaeyserm/www/fccee/mc_theta_plus.png")



if __name__ == "__main__":
    main()


